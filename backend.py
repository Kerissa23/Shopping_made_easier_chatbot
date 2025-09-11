from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from groq import Groq

from utils import parse_query_to_keywords, parse_price, classify_intent
from flipkart import get_flipkart_data
from myntra import get_myntra_data
from snapdeal import get_snapdeal_data

# Load environment variables
load_dotenv('.env.sh')
client = Groq(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="ShopSmart AI Backend")

# -------------------------------
# Helper: LLM product analysis
# -------------------------------
def analyze_with_llm(user_message, products):
    product_descriptions = "\n".join(
        [f"{i+1}. {p['title']} - {p['price']} ({p['source']})"
         for i, p in enumerate(products)]
    )

    prompt = f"""
    You are a shopping assistant. 
    User message: "{user_message}"
    Here are the products currently in database:
    {product_descriptions}

    If the user asks about specific product numbers, describe them.
    If they ask for comparisons, filter accordingly.
    Always use only the products listed above.
    If there are no products in the database according to the user message, just respond with 'Null'.
    If the user is asking for more, just respond with 'More'.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a shopping assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


# -------------------------------
# Request/Response Schemas
# -------------------------------
class ChatInput(BaseModel):
    user_message: str  # frontend always sends this

class ChatResponse(BaseModel):
    bot_message: str
    products: List[Dict[str, Any]]


# -------------------------------
# In-memory session state
# -------------------------------
temp_db = {"products": [], "counter": 0}
chat_history = []
last_results = []


# -------------------------------
# Chat Endpoint
# -------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(input_data: ChatInput):
    try:
        print("DEBUG raw input:", input_data.dict())
        global last_results, temp_db, chat_history

        user_message = input_data.user_message.strip().lower()
        print(user_message)

        # --- Check product references ---
        if "first product" in user_message or "1st product" in user_message:
            index = 0
        elif "second product" in user_message or "2nd product" in user_message:
            index = 1
        elif "third product" in user_message or "3rd product" in user_message:
            index = 2
        else:
            index = None

        if index is not None and last_results:
            if index < len(last_results):
                product = last_results[index]
                bot_message = (
                    f"Here’s more about the {['first','second','third'][index]} product:\n\n"
                    f"**{product.get('title')}**\n"
                    f"Price: {product.get('price')}\n"
                    f"Source: {product.get('source')}\n"
                    f"Link: {product.get('link')}\n"
                )
                return ChatResponse(bot_message=bot_message, products=[product])
            else:
                return ChatResponse(bot_message="That product number doesn’t exist in the current results.", products=[])

        # --- Classify intent ---
        intent = classify_intent(user_message)

        if intent == "product_search":
            # Reuse temp DB if not too old
            if temp_db["products"] and temp_db["counter"] < 10:
                description = analyze_with_llm(user_message, temp_db["products"])
                if description not in ("Null", "More"):
                    keywords = parse_query_to_keywords(user_message, chat_history)
                    chat_history.append(keywords)
                    temp_db["counter"] += 1
                    return ChatResponse(bot_message=description, products=temp_db["products"])

            # Otherwise fetch new products
            keywords = parse_query_to_keywords(user_message, chat_history)
            chat_history.append(keywords)
            flipkart_products = get_flipkart_data(keywords)
            myntra_products = get_myntra_data(keywords)
            snapdeal_products = get_snapdeal_data(keywords)

            all_products = flipkart_products + myntra_products + snapdeal_products
            balanced_initial_view = []
            balanced_initial_view.extend(flipkart_products[:5])
            balanced_initial_view.extend(myntra_products[:5])
            balanced_initial_view.extend(snapdeal_products[:5])
            products_to_display = balanced_initial_view
            products_to_display.sort(key=lambda p: parse_price(p.get('price')))

            # Save to temp DB
            temp_db["products"] = products_to_display[:15]
            last_results = products_to_display[:15]
            temp_db["counter"] = 1

            bot_message = f"I found {len(all_products)} products for '{keywords}'. Here are the top results."
            return ChatResponse(bot_message=bot_message, products=temp_db["products"])

        # --- General Chat ---
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message},
            ],
        )
        bot_response = completion.choices[0].message.content
        return ChatResponse(bot_message=bot_response, products=[])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# Serve Frontend
# -------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return FileResponse('templates/index.html')


if __name__ == "__main__":
    import uvicorn
    print("--- Starting ShopSmart AI Assistant ---")
    print("Your chatbot will be available at: http://127.0.0.1:8000")
    if not os.path.exists(".env.sh"):
        print("\nFATAL ERROR: '.env.sh' not found.")
    else:
        uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)
