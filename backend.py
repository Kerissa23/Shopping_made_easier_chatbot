import os
import re
import shutil
import time
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from flipkart import get_flipkart_data
from myntra import get_myntra_data
from snapdeal import get_snapdeal_data
from utils import parse_query_to_keywords, get_llm, classify_intent

app = FastAPI(title="ShopSmart AI Backend")

# --- Data Models ---
class ChatState(BaseModel):
    session_products: List[Dict[str, Any]] = []
    current_view: List[Dict[str, Any]] = []
    display_offset: int = 0
    chat_history: List[tuple[str, str]] = []

class ChatRequest(BaseModel):
    message: str
    state: ChatState

class ChatResponse(BaseModel):
    bot_message: str
    products_to_display: List[Dict[str, Any]]
    new_state: ChatState

# --- Business Logic ---
def parse_price(price_str: Optional[str]) -> int:
    if not isinstance(price_str, str): return float('inf')
    cleaned_price = re.sub(r'[^\d.]', '', price_str)
    try: return int(float(cleaned_price))
    except (ValueError, TypeError): return float('inf')

# --- Main API Endpoint ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_message = request.message
    state = request.state
    
    print(f"\nReceived message: '{user_message}'")
    
    # --- FIX: Handle greetings and farewells before parsing keywords ---
    intent = classify_intent(user_message, state.chat_history)

    user_msg_lower = user_message.lower().strip()

    if intent == "greeting":
        bot_message = "Hello! What can I help you find today?"
        state.chat_history.append((user_message, bot_message))
        return ChatResponse(
            bot_message=bot_message,
            products_to_display=[],
            new_state=state
        )
    
    elif intent == "farewell":
        bot_message = "Goodbye! Happy shopping!"
        state.chat_history.append((user_message, bot_message))
        return ChatResponse(
            bot_message=bot_message,
            products_to_display=[],
            new_state=state
        )
    elif intent == 'generic_query':
        bot_message = "I'm your personal shopping assistant! To help you find what you need, here are some trending products to get you started."
        keywords = "trending products"  # Default search for generic questions
        
        print(f"Handling generic query. Searching for default keywords: '{keywords}'...")
        flipkart_products = get_flipkart_data(keywords)
        myntra_products = get_myntra_data(keywords)
        snapdeal_products = get_snapdeal_data(keywords)
        
        state.session_products = flipkart_products + myntra_products + snapdeal_products
        state.current_view = state.session_products
        state.display_offset = 0

        if not state.session_products:
            bot_message = "Sorry, I couldn't find any products for that search."
        else:
            balanced_initial_view = []
        balanced_initial_view.extend(flipkart_products[:5])
        balanced_initial_view.extend(myntra_products[:5])
        balanced_initial_view.extend(snapdeal_products[:5])
        products_to_display = balanced_initial_view
        #bot_message = f"I found {len(state.session_products)} products! Here are the top results."
        
        products_to_display.sort(key=lambda p: parse_price(p.get('price')))
        state.display_offset = len(products_to_display)
        state.chat_history.append((user_message, bot_message))

        return ChatResponse(
            bot_message=bot_message,
            products_to_display=products_to_display,
            new_state=state
        )

    bot_message = ""
    products_to_display = []
    PAGE_SIZE = 15

    is_new_search = "more" not in user_message.lower()

    if is_new_search or not state.session_products:
        keywords = parse_query_to_keywords(user_message, state.chat_history)
        print(f"Starting new search for: '{keywords}'...")
        
        flipkart_products = get_flipkart_data(keywords)
        myntra_products = get_myntra_data(keywords)
        snapdeal_products = get_snapdeal_data(keywords)
        
        state.session_products = flipkart_products + myntra_products + snapdeal_products
        state.current_view = state.session_products
        state.display_offset = 0

        if not state.session_products:
            bot_message = "Sorry, I couldn't find any products for that search."
        else:
            balanced_initial_view = []
            balanced_initial_view.extend(flipkart_products[:5])
            balanced_initial_view.extend(myntra_products[:5])
            balanced_initial_view.extend(snapdeal_products[:5])
            products_to_display = balanced_initial_view
            bot_message = f"I found {len(state.session_products)} products! Here are the top results."
            state.display_offset = len(products_to_display)
            
    else: 
        if "more" in user_message.lower():
            print(f"Showing more results from the current view of {len(state.current_view)} products...")
            if state.display_offset >= len(state.current_view):
                bot_message = "You've seen all the results for this view!"
            else:
                end_offset = state.display_offset + PAGE_SIZE
                products_to_display = state.current_view[state.display_offset:end_offset]
                state.display_offset = end_offset
                bot_message = "Here are the next results:"
        else:
             bot_message = "Sorry, I'm not sure how to handle that. Please try a new search."


    if not products_to_display and not bot_message:
        bot_message = "Sorry, I couldn't find any products that match your specific request."
    
    products_to_display.sort(key=lambda p: parse_price(p.get('price')))
    
    state.chat_history.append((user_message, bot_message))

    return ChatResponse(
        bot_message=bot_message,
        products_to_display=products_to_display,
        new_state=state
    )

# --- Serve Static Files ---
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return FileResponse('templates/index.html')

if __name__ == '__main__':
    import uvicorn
    print("--- Starting ShopSmart AI Assistant ---")
    print("Your chatbot will be available at: http://127.0.0.1:8000")
    if not os.path.exists(".env.sh"):
        print("\nFATAL ERROR: '.env.sh' not found.")
    else:
        uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)