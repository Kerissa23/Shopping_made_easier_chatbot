from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
import json
import re

load_dotenv('.env.sh')

def get_llm():
    """Creates and returns the base language model instance."""
    return ChatOpenAI(
        model_name="llama3-70b-8192",
        temperature=0.0,
        verbose=True,
    )

def parse_query_to_keywords(query, chat_history):
    """
    Uses the LLM to extract key search terms from a user's query,
    considering the conversation history. This replaces the more complex
    intent parsing to match the logic from main.py.
    """
    parsing_prompt_template = """
    You are a search query optimizer for a shopping bot.
    Your task is to extract the essential product keywords from the user's latest query.
    Consider the chat history for context, but the output should be a clean search query based on the LATEST request.

    **Chat History:**
    {chat_history}

    **Latest User Query:** "{user_query}"

    Respond ONLY with the optimized search keywords.

    --- EXAMPLES ---
    History: [] | Query: "show me red running shoes for men size 10" -> "red running shoes men size 10"
    History: [("running shoes", "...")] | Query: "what about in blue?" -> "blue running shoes"
    History: [("laptops", "...")] | Query: "only show ones with 16gb ram" -> "laptops with 16gb ram"
    """
    
    llm = get_llm()
    history_str = "\n".join([f"Human: {q}\nAI: {a}" for q, a in chat_history])
    prompt = parsing_prompt_template.format(user_query=query, chat_history=history_str)
    
    try:
        response = llm.invoke(prompt)
        keywords = response.content.strip().replace('"', '')
        print(f"LLM successfully parsed keywords as: '{keywords}'")
        return keywords
    except Exception as e:
        print(f"Error during keyword parsing: {e}. Defaulting to original query.")
        return query
    
def classify_intent(query, chat_history):
    """
    Uses an LLM to classify the user's intent to handle generic questions.
    """
    intent_prompt_template = """
    You are an intent classification model for a shopping assistant.
    Your task is to classify the user's latest message into one of the following categories:
    'greeting', 'farewell', 'product_search', 'generic_query'.

    - 'greeting': For hellos, hi, etc.
    - 'farewell': For goodbyes, bye, etc.
    - 'product_search': For any query asking for products, brands, or item types.
    - 'generic_query': For conversational questions not related to shopping (e.g., "how are you?", "what is your purpose?", "tell me a joke").

    **Chat History (for context):**
    {chat_history}

    **Latest User Query:** "{user_query}"

    Respond ONLY with the classification label (e.g., 'product_search', 'generic_query').
    ---
    Query: "hi there" -> 'greeting'
    Query: "show me some nike shoes" -> 'product_search'
    Query: "how are you today?" -> 'generic_query'
    Query: "thanks bye" -> 'farewell'
    Query: "got any laptops?" -> 'product_search'
    Query: "for girls" -> 'product_search'
    Query: "what are you doing" -> 'generic_query'
    """
    llm = get_llm()
    history_str = "\n".join([f"Human: {q}\nAI: {a}" for q, a in chat_history])
    prompt = intent_prompt_template.format(user_query=query, chat_history=history_str)
    
    try:
        response = llm.invoke(prompt)
        intent = response.content.strip().replace("'", "")
        print(f"LLM classified intent as: '{intent}'")
        if intent in ['greeting', 'farewell', 'product_search', 'generic_query']:
            return intent
        return 'product_search' # Default to search if classification is unclear
    except Exception as e:
        print(f"Error during intent classification: {e}. Defaulting to 'product_search'.")
        return 'product_search'
