
import os
import shutil
from flipkart import get_flipkart_data
from myntra import get_myntra_data
from snapdeal import get_snapdeal_data
from utils import get_response, get_chroma_client
from text_to_doc import get_doc_chunks

def clear_vector_store():
    """
    Clears the Chroma vector store by deleting the persistence directory.
    This ensures that each user query starts with a fresh context.
    """
    persist_directory = "data/chroma"
    if os.path.exists(persist_directory):
        print("Clearing previous product data...")
        try:
            shutil.rmtree(persist_directory)
            print("Previous data cleared successfully.")
        except OSError as e:
            print(f"Error clearing vector store: {e}")

def shopping_chatbot():
    """
    Main function to run the interactive shopping chatbot.
    """
    while True:
        query = input("\nHello! What product are you looking for today? (Type 'exit' to quit)\n> ")
        if query.lower() == 'exit':
            print("\nGoodbye! Happy shopping!")
            break

        print(f"\nSearching for '{query}' on Flipkart, Myntra, and Snapdeal...")

        # Step 1: Fetch data from all e-commerce sources
        try:
            flipkart_products = get_flipkart_data(query)
            myntra_products = get_myntra_data(query)
            snapdeal_products = get_snapdeal_data(query)
        except Exception as e:
            print(f"An error occurred while fetching product data: {e}")
            print("Please ensure your SERPAPI_API_KEY is valid and has credits.")
            continue

        all_products = flipkart_products + myntra_products + snapdeal_products
        
        if not all_products:
            print("\nSorry, I couldn't find any products matching your query. Please try a different search.")
            continue
        
        print(f"Found a total of {len(all_products)} products. Processing...")

        # Step 2: Clear old data and prepare for new context
        clear_vector_store()
        vector_store = get_chroma_client()

        # Step 3: Format the fetched product data into a single string for the LLM
        context_string = ""
        for product in all_products:
            # Myntra's scraper has a different output structure, so we handle it separately
            if 'snippet' in product:
                price = "N/A"
                # Attempt to extract price from the snippet text for Myntra products
                if product.get('snippet') and 'Rs.' in product['snippet']:
                    try:
                        price_text = product['snippet'].split('Rs.')[1].strip().split(' ')[0]
                        price = f"₹{price_text.replace(',', '')}"
                    except (IndexError, ValueError):
                        price = "N/A" # Fallback if parsing fails
                
                context_string += f"Title: {product.get('title', 'N/A')}\nPrice: {price}\nLink: {product.get('link', 'N/A')}\nSource: Myntra\n\n"
            else:
                context_string += f"Title: {product.get('title', 'N/A')}\nPrice: {product.get('price', 'N/A')}\nLink: {product.get('link', 'N/A')}\nSource: {product.get('source', 'N/A')}\n\n"

        # Step 4: Convert the context string into documents and store them in the vector database
        metadata = {"source": "ecommerce_search_results"}
        doc_chunks = get_doc_chunks(context_string, metadata)
        
        vector_store.add_documents(doc_chunks)
        vector_store.persist()
        
        print("Asking the AI assistant to compare and present the best options...")

        # Step 5: Call the LLM chain to get a user-friendly, tabulated response
        try:
            answer = get_response(query)
            print("\n=======================================")
            print("   Your Personal Shopping Results")
            print("=======================================\n")
            print(answer)
            print("\n=======================================\n")
        except Exception as e:
            print(f"\nAn error occurred while generating the response: {e}")
            print("This could be due to an issue with the OpenAI API key or the model configuration.")
            print("Please check your .env.sh file and ensure all required keys are set correctly.")

def check_env_file():
    """
    Checks for the existence of the .env.sh file and provides instructions if it's missing.
    """
    if not os.path.exists(".env.sh"):
        print("---" * 20)
        print("ERROR: Environment file '.env.sh' not found.")
        print("This file is required to store your API keys.")
        print("\nPlease create a file named '.env.sh' in the same directory and add the following lines:")
        print('\nexport SERPAPI_API_KEY="your_serpapi_api_key_here"')
        print('export OPENAI_API_KEY="your_openai_or_groq_api_key_here"\n')
        print("---" * 20)
        return False
    return True

if __name__ == "__main__":
    if check_env_file():
        shopping_chatbot()