from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
import json
import re
import chromadb
from chromadb.utils import embedding_functions
import time # Import time for timestamping
import uuid

# Import List and Dict from typing
from typing import List, Dict, Any, Optional

load_dotenv('.env.sh')

# Initialize ChromaDB client
# For a persistent client, you might specify a path: chromadb.PersistentClient(path="./chroma_db")
# For now, we'll use an in-memory client for simplicity, but you can change this.
# client = chromadb.Client() # Changed to persistent client for testing
client = chromadb.PersistentClient(path="./chroma_db") # Using a persistent client

# Default embedding function
default_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Get or create ChromaDB collections
try:
    chat_history_collection = client.get_or_create_collection(
        name="chat_history", 
        embedding_function=default_ef
    )
    print("ChromaDB 'chat_history' collection initialized.")
except Exception as e:
    print(f"Error getting/creating chat_history collection: {e}")
    chat_history_collection = None # Handle error gracefully

try:
    product_collection = client.get_or_create_collection(
        name="product_data", 
        embedding_function=default_ef,
        metadata={"hnsw:space": "cosine"} # Use cosine similarity for product searches
    )
    print("ChromaDB 'product_data' collection initialized.")
except Exception as e:
    print(f"Error getting/creating product_data collection: {e}")
    product_collection = None # Handle error gracefully


def get_llm():
    """Creates and returns the base language model instance."""
    # Ensure you have OPENAI_API_KEY set in .env.sh for this to work
    # Or replace with a different LangChain compatible LLM client
    return ChatOpenAI(
        model_name="gpt-3.5-turbo", # Changed to a more common and faster model for demonstration
        temperature=0.0,
        verbose=True,
    )

def add_message_to_history(sender: str, message: str, message_id: str):
    """Adds a message to the ChromaDB chat history."""
    if chat_history_collection:
        try:
            chat_history_collection.add(
                documents=[f"{sender}: {message}"],
                metadatas=[{"sender": sender, "timestamp": time.time()}], # Store timestamp as float
                ids=[message_id]
            )
            # print(f"Added message '{message_id}' to chat history.")
        except Exception as e:
            print(f"Error adding message to chat history: {e}")

def get_recent_chat_history(num_messages: int = 5) -> str:
    """Retrieves recent chat history from ChromaDB, sorted by timestamp."""
    if chat_history_collection:
        try:
            # Query all documents (or a large enough subset if the collection is huge)
            # and then sort in Python. ChromaDB's query() can't directly sort by metadata yet.
            results = chat_history_collection.get(
                ids=chat_history_collection.get()['ids'], # Get all IDs
                include=['documents', 'metadatas']
            )
            
            # Combine documents and metadatas, then sort by timestamp
            history_items = []
            if results['documents'] and results['metadatas']:
                for doc, meta in zip(results['documents'], results['metadatas']):
                    history_items.append((doc, meta.get('timestamp', 0)))
            
            # Sort by timestamp in ascending order (oldest first)
            history_items.sort(key=lambda x: x[1])
            
            # Take the last 'num_messages' for the most recent history
            recent_history = [item[0] for item in history_items[-num_messages:]]
            
            # print(f"Retrieved recent chat history: {recent_history}")
            return "\n".join(recent_history)
        except Exception as e:
            print(f"Error retrieving chat history from ChromaDB: {e}")
            return ""
    return ""

def add_products_to_chroma(products: list[dict]):
    """Adds a list of product dictionaries to the ChromaDB product collection."""
    if not product_collection:
        print("Product collection not initialized, cannot add products.")
        return

    documents = []
    metadatas = []
    ids = []

    for i, product in enumerate(products):
        # Create a unique ID for each product, perhaps combining source and title/URL
        # Using a hash of the URL is a good way to ensure uniqueness for a product
        product_id = f"{product.get('source', 'unknown')}_{hash(product.get('url', str(uuid.uuid4())))}"
        
        # Create a rich document string for better search
        doc_string = (
            f"Product: {product.get('title', 'N/A')}. "
            f"Price: {product.get('price', 'N/A')}. "
            f"Rating: {product.get('rating', 'N/A')}. "
            f"Source: {product.get('source', 'N/A')}. "
            f"Category: {product.get('category', 'N/A')}. "
            f"Description: {product.get('description', '')}"
        )

        documents.append(doc_string)
        metadatas.append(product) # Store the full product dict as metadata
        ids.append(product_id)

    if documents:
        try:
            # Filter out IDs that already exist to prevent adding duplicates.
            # This is important for a persistent store.
            existing_ids_result = product_collection.get(ids=ids, include=[])
            existing_ids = set(existing_ids_result['ids'])
            
            new_ids = [id_ for id_ in ids if id_ not in existing_ids]
            new_documents = [documents[i] for i, id_ in enumerate(ids) if id_ in new_ids]
            new_metadatas = [metadatas[i] for i, id_ in enumerate(ids) if id_ in new_ids]

            if new_ids:
                product_collection.add(
                    documents=new_documents,
                    metadatas=new_metadatas,
                    ids=new_ids
                )
                print(f"Added {len(new_ids)} new products to product_data collection.")
            else:
                # print("No new products to add to product_data collection (all already exist).")
                pass # Suppress this print to reduce verbosity
        except Exception as e:
            print(f"Error adding products to ChromaDB: {e}")

def get_products_from_chroma(query_keywords: str, n_results: int = 15) -> List[Dict[str, Any]]:
    """Retrieves relevant products from ChromaDB based on query keywords."""
    if not product_collection:
        print("Product collection not initialized, cannot retrieve products.")
        return []

    try:
        # Perform a query based on the keywords
        results = product_collection.query(
            query_texts=[query_keywords],
            n_results=n_results,
            include=['metadatas'] # We want the full product metadata
        )
        
        products = [item for item in results.get('metadatas', [[]])[0] if item is not None]
        print(f"Retrieved {len(products)} products from ChromaDB for query '{query_keywords}'.")
        return products
    except Exception as e:
        print(f"Error querying products from ChromaDB: {e}")
        return []

def parse_query_to_keywords(query: str) -> str:
    """
    Uses the LLM to extract key search terms from a user's query,
    considering the conversation history from ChromaDB.
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
    History: ["Human: running shoes", "AI: ..."] | Query: "what about in blue?" -> "blue running shoes"
    History: ["Human: laptops", "AI: ..."] | Query: "only show ones with 16gb ram" -> "laptops with 16gb ram"
    """
    
    llm = get_llm()
    history_str = get_recent_chat_history(num_messages=5)
    prompt = parsing_prompt_template.format(user_query=query, chat_history=history_str)
    
    try:
        response = llm.invoke(prompt)
        keywords = response.content.strip().replace('"', '')
        print(f"LLM successfully parsed keywords as: '{keywords}'")
        return keywords
    except Exception as e:
        print(f"Error during keyword parsing: {e}. Defaulting to original query.")
        return query
    
def classify_intent(query: str) -> str:
    """
    Uses an LLM to classify the user's intent to handle generic questions,
    considering the conversation history from ChromaDB.
    """
    intent_prompt_template = """
    You are an intent classification model for a shopping assistant.
    Your task is to classify the user's latest message into one of the following categories:
    'greeting', 'farewell', 'product_search', 'generic_query', 'show_more'.

    - 'greeting': For hellos, hi, etc.
    - 'farewell': For goodbyes, bye, etc.
    - 'product_search': For any query asking for products, brands, or item types.
    - 'generic_query': For conversational questions not related to shopping (e.g., "how are you?", "what is your purpose?", "tell me a joke").
    - 'show_more': When the user explicitly asks for more products from the current search results (e.g., "show more", "next page", "more products").

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
    Query: "show more" -> 'show_more'
    Query: "next results" -> 'show_more'
    """
    llm = get_llm()
    history_str = get_recent_chat_history(num_messages=5)
    prompt = intent_prompt_template.format(user_query=query, chat_history=history_str)
    
    try:
        response = llm.invoke(prompt)
        intent = response.content.strip().replace("'", "")
        print(f"LLM classified intent as: '{intent}'")
        if intent in ['greeting', 'farewell', 'product_search', 'generic_query', 'show_more']:
            return intent
        return 'product_search' # Default to search if classification is unclear
    except Exception as e:
        print(f"Error during intent classification: {e}. Defaulting to 'product_search'.")
        return 'product_search'

def generate_bot_response(user_message: str, current_products: List[Dict[str, Any]], chat_history_str: str, intent: str, last_search_keywords: Optional[str] = None) -> str:
    """
    Generates a conversational bot response using the LLM,
    considering user message, current products, chat history, and intent.
    """
    llm = get_llm()

    # Create a summary of current products for the LLM
    product_summary = ""
    if current_products:
        product_summary = "Here are some of the products I found:\n"
        for i, p in enumerate(current_products[:5]): # Summarize top 5 products
            title = p.get('title', 'N/A')
            price = p.get('price', 'N/A')
            source = p.get('source', 'N/A')
            product_summary += f"{i+1}. {title} from {source} for {price}.\n"
        product_summary += f"Total products displayed in this view: {len(current_products)}."
    else:
        product_summary = "No products currently displayed or found for this query."


    response_prompt_template = """
    You are ShopSmart AI, a friendly and helpful shopping assistant.
    Your goal is to assist users in finding products and answer their questions.
    Engage in a natural conversation.

    **Current Context:**
    - User Intent: {intent}
    - Last Search Keywords (if any): {last_search_keywords}
    - Products in Current View:
    {product_summary}

    **Chat History:**
    {chat_history}

    **Latest User Query:** "{user_query}"

    Based on the above information, generate a concise and helpful bot response.
    If the intent is 'product_search', acknowledge the search and mention if products were found.
    If the intent is 'show_more', acknowledge showing more products.
    If it's a 'greeting' or 'farewell', respond appropriately.
    For 'generic_query', respond conversationally.
    If no products were found, clearly state that.
    If products are found, you can mention some of the top ones briefly without listing all details.
    
    Bot: 
    """

    prompt = response_prompt_template.format(
        user_query=user_message,
        chat_history=chat_history_str,
        intent=intent,
        last_search_keywords=last_search_keywords if last_search_keywords else "N/A",
        product_summary=product_summary
    )

    try:
        response = llm.invoke(prompt)
        bot_message = response.content.strip()
        print(f"LLM generated bot response: '{bot_message}'")
        return bot_message
    except Exception as e:
        print(f"Error during bot response generation: {e}. Defaulting to a generic response.")
        return "I'm sorry, I'm having trouble generating a detailed response right now. How else can I assist you?"