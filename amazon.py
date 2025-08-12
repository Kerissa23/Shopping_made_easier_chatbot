from serpapi import GoogleSearch
import os
from dotenv import load_dotenv

load_dotenv('.env.sh')

API_KEY = os.getenv("SERPAPI_API_KEY")

def search_amazon(query):
    params = {
        "engine": "amazon",
        "api_key": API_KEY,
        "amazon_domain": "amazon.in",
        "k": query  # ✅ Must be 'k', not 'search_term'
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    if "error" in results:
        print("Error:", results["error"])
        return []

    products = []
    for item in results.get("organic_results", []):
        price = item.get("price")
        if isinstance(price, dict):
            price = price.get("raw")
        products.append({
            "title": item.get("title"),
            "price": price,
            "link": item.get("link"),
            "source":"Amazon",
            "thumbnail": item.get("thumbnail")
        })
    return products

if __name__ == "__main__":
    query = "tvs"
    data = search_amazon(query)
    for p in data:
        print(f"{p['title']} - {p['price']} - {p['link']}")

