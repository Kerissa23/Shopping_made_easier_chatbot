import os
import requests
from dotenv import load_dotenv

def get_flipkart_data(query):
    # Get API key from environment
    load_dotenv(dotenv_path=".env.sh", override=True)
    API_KEY = os.getenv("SERPAPI_API_KEY")
    params = {
        "engine": "google_shopping",
        "q": query,
        "hl": "en",
        "gl": "in",
        "api_key": API_KEY
    }

    try:
        response = requests.get("https://serpapi.com/search.json", params=params)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print("Request failed:", e)
        return []
    except ValueError:
        print("Invalid JSON response")
        return []

    results = []
    for product in data.get("shopping_results", []):
        link = product.get("link") or product.get("product_link")
        results.append({
            "title": product.get("title"),
            "price": product.get("price"),
            "link": link,
            "source": product.get("source"),
            "thumbnail": product.get("thumbnail")
        })

    return results

# Example usage
if __name__ == "__main__":
    products = get_flipkart_data("redmi phone")
    for p in products:
        print(f"{p['title']} | {p['price']} | {p['link']}")
