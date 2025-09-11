import os
import re
from dotenv import load_dotenv
from groq import Groq

# Load env variables (GROQ_API_KEY must be in .env)
load_dotenv('.env.sh')
client = Groq(api_key=os.getenv("OPENAI_API_KEY"))

# --- Price Parsing Helper ---
def parse_price(price_str):
    """
    Convert a price string like '₹1,299' or '$50.00' into an integer.
    Returns float('inf') if price can't be parsed (so it sorts last).
    """
    if not isinstance(price_str, str):
        return float('inf')
    cleaned_price = re.sub(r"[^\d.]", "", price_str)
    try:
        return int(float(cleaned_price))
    except (ValueError, TypeError):
        return float('inf')

# --- Intent Classification ---
def classify_intent(user_message: str, chat_history: list = []):
    """
    Uses Groq LLM to classify whether the message is:
    - product_search
    - general_chat
    """
    prompt = f"""
    Classify the user input into one of the following intents:
    - product_search: if the user is asking about buying, finding, or looking for products.
    - general_chat: for greetings, questions, or conversation not related to products.

    User message: "{user_message}"
    Answer with exactly one word: product_search or general_chat.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )

    intent = response.choices[0].message.content.strip().lower()

    if intent not in ["product_search", "general_chat"]:
        return "general_chat"  # fallback
    return intent

# --- Keyword Extraction ---
def parse_query_to_keywords(user_message: str, chat_history: list = []):
    """
    Uses Groq LLM to extract key search terms from a query.
    Example: 'I want blue running shoes size 10' → 'blue running shoes size 10'
    """
    prompt = f"""You are a search query optimizer for a shopping bot.
    Your task is to extract the essential product keywords from the user's latest query.
    Consider the chat history for context, but the output should be a clean search query based on the LATEST request.
    If the Latest request is 'More', return the keywords based on latest request in the chat history.
    **Chat History:**
    {chat_history}

    **Latest User Query:** "{user_message}"

    Respond ONLY with the optimized search keywords.

    --- EXAMPLES ---
    History: [] | Query: "show me red running shoes for men size 10" -> "red running shoes men size 10"
    History: ["Human: running shoes", "AI: ..."] | Query: "what about in blue?" -> "blue running shoes"
    History: ["Human: laptops", "AI: ..."] | Query: "only show ones with 16gb ram" -> "laptops with 16gb ram"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )

    keywords = response.choices[0].message.content.strip()
    return keywords if keywords else user_message
