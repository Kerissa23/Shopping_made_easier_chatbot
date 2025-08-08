import os
import requests
from dotenv import load_dotenv
import json
import re

def get_flipkart_product_links(query):
    """
    Fetches direct links to Flipkart products using the DuckDuckGo engine.
    This method reliably gets product links and filters out category/search pages.
    """
    load_dotenv(dotenv_path=".env.sh", override=True)
    API_KEY = os.getenv("SERPAPI_API_KEY")

    if not API_KEY:
        print("Error: SERPAPI_API_KEY not found. Please check your .env.sh file.")
        return []

    # Use the reliable DuckDuckGo engine with a site search.
    params = {
        "api_key": API_KEY,
        "engine": "duckduckgo",
        "q": f"{query} site:flipkart.com"
    }

    try:
        print("Querying SerpApi with the DuckDuckGo engine (with improved filtering)...")
        response = requests.get("https://serpapi.com/search.json", params=params)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []

    organic_results = data.get("organic_results")
    if not organic_results:
        print("Request successful, but no organic results were found.")
        return []

    print("Filtering results to find direct product links...")
    product_links = []
    for result in organic_results:
        link = result.get("link")
        title = result.get("title")

        # --- Intelligent Filtering ---
        # 1. Skip if the link is clearly a search or category page.
        if "/q/" in link or "/pr?" in link or "/stores/" in link:
            continue
        
        # 2. Skip if the link does not look like a modern Flipkart product URL (which often have '/p/').
        if "/p/" not in link:
             continue

        # 3. Skip if the title suggests it's not a single product.
        if "online in india" in title.lower() or "under" in title.lower():
            continue

        product_links.append({
            "title": title.replace("- Flipkart", "").strip(), # Clean up the title
            "link": link,
            "source": "Flipkart"
        })

    return product_links

# Example usage
if __name__ == "__main__":
    products = get_flipkart_product_links("redmi phone")
    if products:
        print(f"\nSuccess! Found {len(products)} direct links to products on Flipkart.")
        for p in products:
            print(f"- Title: {p.get('title')}\n  Source: {p.get('source')}\n  Link: {p.get('link')}\n")
    else:
        print("\nExecution finished. No direct product links could be found.")