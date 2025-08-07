# from utils import get_response, get_chroma_client

# # Storing webpage content into vector store
# # Make sure not to store the same documents twice

# # store_docs("https://www.flipkart.com/")
# from utils import store_multiple_sites

# store_multiple_sites([
#     "https://www.flipkart.com/search?q=phones+20000+to+30000",
#     "https://www.amazon.in/s?k=phones+20000+to+30000"
# ])

# # Setting up organization information

# organization_name = "Flipkart"
# organization_info = "Shopping Website for clothes and accesories"
# contact_info = """Email: reachus@cloudxlab.com 
# India Phone: +9108049202224
# International Phone: +1 (412) 568-3901.
# Raise a query: https://cloudxlab.com/reach-us-queries
# Forum: https://discuss.cloudxlab.com/"""

# response = get_response("List latest mobiles in the range of 20,000 - 30,000", organization_name, organization_info, contact_info)
# print("Answer:", response)
#----------------
from utils import get_response, store_multiple_sites
import urllib.parse

def run_chatbot():
    """
    Runs the main chatbot loop.
    """
    print("Welcome to the Shopping Assistant Chatbot!")
    print("I can search for products on Flipkart, Myntra, and Snapdeal.")
    print("For example, try 'running shoes under 3000' or 't-shirts'. Type 'exit' to quit.")

    while True:
        user_query = input("\nYour prompt: ")
        if user_query.lower() == 'exit':
            break

        encoded_query = urllib.parse.quote_plus(user_query)

        urls_to_scrape = [
            f"https://www.flipkart.com/search?q={encoded_query}",
            f"https://www.myntra.com/search?q={encoded_query}",
            f"https://www.snapdeal.com/search?keyword={encoded_query}",
        ]

        print("\nSearching for products...")
        # Pass the user_query to the scraping and storing function
        store_multiple_sites(urls_to_scrape, user_query)
        print("Scraping complete.")
        
        ai_question = f"Please find products related to '{user_query}' from the scraped data. Present the results you find in a table, sorted by price."
        
        response = get_response(ai_question)
        print("\nAnswer:", response)

if __name__ == "__main__":
    run_chatbot()