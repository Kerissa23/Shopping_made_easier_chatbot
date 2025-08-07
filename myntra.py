import os
import requests
from dotenv import load_dotenv

def get_myntra_data(query):
    # Load API key from .env.sh
    load_dotenv(dotenv_path=".env.sh", override=True)
    API_KEY = os.getenv("SERPAPI_API_KEY")

    # Set query parameters
    params = {
        "engine": "google",
        "q": f"{query} site:myntra.com",
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
    for result in data.get("organic_results", []):
        link = result.get("link")
        if link and "myntra.com" in link:
            results.append({
                "title": result.get("title"),
                "link": link,
                "snippet": result.get("snippet"),
                "thumbnail": result.get("thumbnail")  # not always available
            })

    return results

# Example usage
if __name__ == "__main__":
    products = get_myntra_data("t-shirts")
    for p in products:
        print(f"{p['title']} | {p['link']}")
