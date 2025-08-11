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

def parse_user_intent(query, chat_history):
    """
    Uses the LLM to determine user intent: new search, filter, show more, or unsupported.
    """
    parsing_prompt_template = """
    You are an expert query analyzer for a shopping bot. Your task is to determine the user's intent based on their latest query and the chat history.
    The intent can be one of four things:
    1. "new_search": The user is starting a new search for a different product, or is fundamentally changing the criteria of the last search (like price).
    2. "filter_results": The user is asking to refine the *previous* search results by a simple criteria (like a store name).
    3. "show_more": The user is asking for "more suggestions", "next", etc.
    4. "unsupported": The query is a greeting, a thank you, or unrelated to shopping.

    Analyze the context below:
    **Chat History:**
    {chat_history}
    
    **Latest User Query:** "{user_query}"
    
    Respond ONLY with a JSON object.
    For "new_search", the value MUST be an optimized search query.
    For "filter_results", the value MUST be a single keyword to filter by (e.g., "flipkart").
    
    {{
      "intent": "new_search" | "filter_results" | "show_more" | "unsupported",
      "value": "The search query, filter keyword, or null"
    }}

    --- EXAMPLES ---
    Query: "hi" -> {{"intent": "unsupported", "value": null}}
    Query: "pink kurtas for women" -> {{"intent": "new_search", "value": "pink kurtas for women"}}
    
    History: [("pink kurtas", "...")] | Query: "from myntra" -> {{"intent": "filter_results", "value": "myntra"}}
    History: [("pink kurtas", "...")] | Query: "more suggestions" -> {{"intent": "show_more", "value": null}}
    
    History: [("pink kurtas", "...")] | Query: "above 500" -> {{"intent": "new_search", "value": "pink kurtas above 500"}}
    History: [("pink kurtas", "...")] | Query: "what about in blue" -> {{"intent": "new_search", "value": "blue kurtas"}}
    """
    
    llm = get_llm()
    history_str = "\n".join([f"Human: {q}\nAI: {a}" for q, a in chat_history])
    parsing_prompt = parsing_prompt_template.format(user_query=query, chat_history=history_str)
    
    response = llm.invoke(parsing_prompt)
    
    try:
        json_string = re.search(r'\{.*\}', response.content, re.DOTALL).group()
        parsed_data = json.loads(json_string)
        print(f"LLM successfully parsed intent as: {parsed_data}")
        return parsed_data
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error parsing LLM intent: {e}. Defaulting to new search.")
        return {"intent": "new_search", "value": query}

# Remove unused functions to simplify the file
# get_chroma_client, make_chain, get_response are not used by the backend.