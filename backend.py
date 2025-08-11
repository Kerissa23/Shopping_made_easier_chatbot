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
from utils import parse_user_intent, get_llm

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

# --- NEW AI-POWERED FILTER ---
def filter_products_with_llm(products, filter_query):
    """Uses the LLM to intelligently filter a list of products based on a natural language query."""
    print(f"\nIntelligently filtering {len(products)} products for: '{filter_query}'...")
    llm = get_llm()
    # Create a simplified context string with just titles and their original index
    context = "\n".join([f"Item {i+1}: {p.get('title')}" for i, p in enumerate(products)])
    
    prompt = f"""You are a master list filter. From the 'Product List' below, return a comma-separated list of the item numbers that are a strong match for the 'Filter Request'.

**Filter Request:**
{filter_query}
    
**Product List:**
{context}

Respond ONLY with the comma-separated numbers. Example: 1, 3, 15"""
    
    response = llm.invoke(prompt)
    try:
        # Extract numbers from the response string and convert to zero-based indices
        relevant_indices = [int(i.strip()) - 1 for i in response.content.split(',') if i.strip().isdigit()]
        # Create the new list based on the indices the LLM chose
        filtered_products = [products[i] for i in relevant_indices if 0 <= i < len(products)]
        print(f"LLM filtering found {len(filtered_products)} relevant products.")
        return filtered_products
    except Exception as e:
        print(f"Error during LLM filtering: {e}. Returning an empty list.")
        return []

# --- Main API Endpoint ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_message = request.message
    state = request.state
    
    print(f"\nReceived message: '{user_message}'")
    
    parsed_intent = parse_user_intent(user_message, state.chat_history)
    intent = parsed_intent.get("intent")
    value = parsed_intent.get("value")

    bot_message = ""
    products_to_display = []
    PAGE_SIZE = 9

    if intent == "new_search":
        print(f"Starting new search for: '{value}'...")
        flipkart = get_flipkart_data(value)
        myntra = get_myntra_data(value)
        snapdeal = get_snapdeal_data(value)
        
        state.session_products = flipkart + myntra + snapdeal
        
        balanced_view = []
        balanced_view.extend(flipkart[:3])
        balanced_view.extend(myntra[:3])
        balanced_view.extend(snapdeal[:3])
        
        state.current_view = state.session_products
        state.display_offset = len(balanced_view)
        products_to_display = balanced_view
        
        if not state.session_products:
            bot_message = "Sorry, I couldn't find any products for that search."
        else:
            bot_message = f"I found {len(state.session_products)} products! Here are the top results:"

    elif intent == "filter_results":
        if not state.session_products:
            bot_message = "I don't have results to filter. Please start a new search."
        else:
            # --- USE THE NEW AI FILTER ---
            filtered_view = filter_products_with_llm(state.session_products, value)
            state.current_view = filtered_view
            state.display_offset = 0
            
            products_to_display = state.current_view[:PAGE_SIZE]
            state.display_offset = len(products_to_display)
            bot_message = f"Okay, here are the results that match '{value}':"

    elif intent == "show_more":
        if not state.current_view:
            bot_message = "There's nothing to show more of. Please start a new search."
        elif state.display_offset >= len(state.current_view):
            bot_message = "You've seen all the results for this view!"
        else:
            end_offset = state.display_offset + PAGE_SIZE
            products_to_display = state.current_view[state.display_offset:end_offset]
            state.display_offset = end_offset
            bot_message = "Here are the next results:"
    
    elif intent == "unsupported":
        bot_message = "I am a shopping assistant. How can I help you find a product?"

    if not products_to_display and intent not in ["unsupported"]:
        bot_message = "Sorry, I couldn't find any products that match your specific request."
    
    products_to_display.sort(key=lambda p: parse_price(p.get('price')))
    
    # Update chat history in the state
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