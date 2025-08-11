import os
import re
import shutil
import time
from flipkart import get_flipkart_data
from myntra import get_myntra_data
from snapdeal import get_snapdeal_data
from utils import get_response, get_chroma_client, parse_query_to_keywords
from text_to_doc import get_doc_chunks

def clear_vector_store():
    """Clears the Chroma vector store."""
    persist_directory = "data/chroma"
    if os.path.exists(persist_directory):
        try:
            time.sleep(0.1)
            shutil.rmtree(persist_directory)
        except OSError as e:
            print(f"Warning: Could not clear vector store: {e}")

def present_results(products_to_show, original_query, chat_history):
    """Takes a list of products and gets a final, formatted response from the LLM."""
    if not products_to_show:
        print("\nSorry, no products matched your specific request.")
        return "Sorry, no products matched your specific request."

    print(f"Formatting {len(products_to_show)} products for presentation...")
    
    clear_vector_store()
    vector_store = get_chroma_client()
    
    context_string = ""
    for product in products_to_show:
        context_string += (
            f"Title: {product.get('title', 'N/A')}\n"
            f"Price: {product.get('price', 'N/A')}\n"
            f"Link: {product.get('link', 'N/A')}\n"
            f"Source: {product.get('source', 'N/A')}\n\n"
        )

    metadata = {"source": "ecommerce_search_results"}
    doc_chunks = get_doc_chunks(context_string, metadata)
    vector_store.add_documents(doc_chunks)
    vector_store.persist()
    
    print("Asking the AI assistant to create the final table...")
    answer = get_response(original_query, chat_history)
    
    print("\n=======================================")
    print("   Your Personal Shopping Results")
    print("=======================================\n")
    print(answer)
    print("\n=======================================\n")
    return answer

def shopping_chatbot():
    """
    Main function for a stateful chatbot that shows balanced initial results.
    """
    chat_history = []
    # --- STATE MANAGEMENT ---
    session_products = []  # Holds the master list from the last new search
    current_view = []      # Holds the currently filtered list
    display_offset = 0     # Tracks pagination
    PAGE_SIZE = 15         # Show a larger page

    while True:
        query = input("\nHello! What can I help you find today? (Type 'exit' to quit)\n> ")
        if query.lower() == 'exit':
            print("\nGoodbye! Happy shopping!")
            break

        print("\nUnderstanding your request...")
        # A simple but effective way to detect if it's a new search vs. a follow-up
        is_new_search = "more" not in query.lower() and "from" not in query.lower() and "only" not in query.lower()

        if is_new_search or not session_products:
            keywords = parse_query_to_keywords(query, chat_history)
            print(f"Starting new search for: '{keywords}'...")
            
            flipkart_products = get_flipkart_data(keywords)
            myntra_products = get_myntra_data(keywords)
            snapdeal_products = get_snapdeal_data(keywords)
            
            # The full, unordered list is saved as the master session list
            session_products = flipkart_products + myntra_products + snapdeal_products
            
            # --- NEW BALANCED VIEW LOGIC ---
            # Create a special view for the first page that is balanced
            balanced_initial_view = []
            balanced_initial_view.extend(flipkart_products[:5])
            balanced_initial_view.extend(myntra_products[:5])
            balanced_initial_view.extend(snapdeal_products[:5])
            
            current_view = session_products # The "true" view is still the full list
            display_offset = 0

            if not session_products:
                print("\nSorry, I couldn't find any products for that search.")
                chat_history.append((query, "I couldn't find any products."))
                continue

            # Present the special balanced list first
            final_answer = present_results(balanced_initial_view, query, chat_history)
            chat_history.append((query, final_answer))
            # The offset is not advanced here, so "more" will show from the top of the full list

        else: # This block handles all follow-up requests ("from myntra", "more", etc.)
            
            if "more" in query.lower():
                print(f"Showing more results from the current view of {len(current_view)} products...")
                if display_offset >= len(current_view):
                    print("\nThere are no more results to show!")
                    final_answer = "There are no more results to show from your last search."
                else:
                    products_to_display = current_view[display_offset:display_offset + PAGE_SIZE]
                    final_answer = present_results(products_to_display, query, chat_history)
                    display_offset += len(products_to_display)
                chat_history.append((query, final_answer))
            
            else: # Handle filtering by source (e.g., "from flipkart")
                # Extract just the brand name
                filter_term = query.lower().replace("from", "").replace("only", "").strip()
                print(f"Applying filter: '{filter_term}' to the {len(session_products)} products found...")
                
                # Filter the MASTER list, not the potentially already filtered view
                current_view = [p for p in session_products if filter_term in p.get('source', '').lower()]
                display_offset = 0 # Reset pagination for the new filtered view

                products_to_display = current_view[display_offset:display_offset + PAGE_SIZE]
                final_answer = present_results(products_to_display, query, chat_history)
                chat_history.append((query, final_answer))
                display_offset += len(products_to_display)


def check_env_file():
    """Checks for the existence of the .env.sh file."""
    if not os.path.exists(".env.sh"):
        print("---" * 20)
        print("ERROR: Environment file '.env.sh' not found.")
        print("\nPlease create a file named '.env.sh' in the same directory and add the following line:")
        print('export OPENAI_API_KEY="your_openai_or_groq_api_key_here"\n')
        print("---" * 20)
        return False
    return True

if __name__ == "__main__":
    if check_env_file():
        shopping_chatbot()