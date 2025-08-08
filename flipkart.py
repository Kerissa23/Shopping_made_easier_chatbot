import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_flipkart_data(query):
    """
    Scrape Flipkart products for any category (electronics, fashion, beauty, groceries, etc.)
    Returns clean short URLs and proper thumbnails.
    """
    search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }

    try:
        print(f"Fetching Flipkart page for '{query}'...")
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch Flipkart page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    
    # Handle multiple product card layouts
    product_blocks = soup.select(
        "div._2kHMtA, div._4ddWXP, div.cPHDOP, div._2B099V, div._1xHGtK, div.slAVV4"
    )

    if not product_blocks:
        print("No product blocks found. Flipkart’s structure might have changed.")
        return []
        
    results = []
    base_url = "https://www.flipkart.com"
    
    print(f"Found {len(product_blocks)} product blocks. Parsing...")
    for block in product_blocks:
        # Title selector (electronics, fashion, beauty, grocery)

        title_element = block.select_one(
            "a.WKTcLC"
        )
        if not title_element:
            title_element = block.select_one(
                "div._4rR01T, div.KzDlHZ, a.s1Q9rs, a.IRpwTa, a.WKTcLC, a.rPDeLR, a.kqCjDq, a.wjcEIp, ._75nlfW .WKTcLC"
            )
        
        # Price selector
        price_element = block.select_one(
            "div._30jeq3, div.Nx9bqj, div._30jeq3._1_WHN1, div._3exPp9"
        )
        
        # Link selector
        link_element = block.select_one(
            "a._1fQZEK, a.s1Q9rs, a.CGtC98, a.IRpwTa, a.WKTcLC, a.rPDeLR, a.kqCjDq, a.DMMoT0"
        )

        # Image selector (handle lazy loading)
        image_element = block.select_one(
            "img._396cs4, img._2r_T1I, img.DByuf4, img._53J4C-, img._3exPp9"
        )
        thumbnail = "N/A"
        if image_element:
            thumbnail = (
                image_element.get('data-src') or
                image_element.get('src') or
                image_element.get('srcset', '').split(" ")[0]
            )
            if thumbnail and not thumbnail.startswith("http"):
                thumbnail = urljoin(base_url, thumbnail)

        # Only include valid products
        if title_element and price_element and link_element:
            raw_link = urljoin(base_url, link_element.get('href', ''))
            short_link = raw_link.split('?')[0]
            if '/p/' in short_link:
                results.append({
                    "title": title_element.get_text(strip=True),
                    "price": price_element.get_text(strip=True),
                    "link": short_link,
                    "source": "Flipkart",
                    "thumbnail": thumbnail
                })

    return results

# --- Test the function ---
if __name__ == "__main__":
    for keyword in ["tv", "phone", "shoes", "perfume", "kurta", "sofa"]:
        print(f"\n=== Searching for '{keyword}' ===")
        products = get_flipkart_data(keyword)
        if products:
            print(f"Found {len(products)} products.")
            for p in products[:5]:
                print(f"{p['title']} | {p['price']} | {p['link']} | {p['thumbnail']}")
        else:
            print("No products found.")
