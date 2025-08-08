import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_flipkart_data(query):
    """
    Gets specific product data from Flipkart using requests/BeautifulSoup.
    This version returns clean, short URLs for the products.
    """
    search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }

    try:
        print(f"Fetching Flipkart page for '{query}'...")
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch Flipkart page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    
    product_blocks = soup.select("div._2kHMtA, div._4ddWXP, div.cPHDOP")

    if not product_blocks:
        print("Could not find any product blocks — Flipkart’s structure may have changed.")
        return []
        
    results = []
    base_url = "https://www.flipkart.com"
    
    print(f"Found {len(product_blocks)} potential product blocks. Parsing...")
    for block in product_blocks:
        title_element = block.select_one("._4rR01T, .s1Q9rs, .KzDlHZ")
        price_element = block.select_one("._30jeq3, .Nx9bqj._4b5DiR")
        link_element = block.select_one("a._1fQZEK, a.s1Q9rs, a.CGtC98")
        
        image_element = block.select_one("img._396cs4, img._2r_T1I, img.DByuf4")
        thumbnail = 'N/A'
        if image_element:
            thumbnail = (
                image_element.get('data-src') or
                image_element.get('src') or
                image_element.get('srcset', '').split(" ")[0]
            )
            if thumbnail and not thumbnail.startswith("http"):
                thumbnail = urljoin(base_url, thumbnail)

        if title_element and price_element and link_element and link_element.has_attr('href'):
            # Get the full, long URL
            raw_link = urljoin(base_url, link_element['href'])
            
            # --- THIS IS THE NEW, CORRECTED PART FOR THE LINK ---
            # Shorten the link by removing all tracking parameters after the '?'
            short_link = raw_link.split('?')[0]
            
            if '/p/' in short_link:  # Only add valid product pages
                results.append({
                    "title": title_element.get_text(strip=True),
                    "price": price_element.get_text(strip=True),
                    "link": short_link, # Use the new, short link
                    "source": "Flipkart",
                    "thumbnail": thumbnail
                })

    return results

# Example usage
if __name__ == "__main__":
    products = get_flipkart_data("TV")
    
    if products:
        print(f"\nSuccessfully parsed {len(products)} products from Flipkart:")
        for p in products[:5]:
            print("-" * 20)
            print(f"Title:     {p['title']}")
            print(f"Price:     {p['price']}")
            print(f"Link:      {p['link']}") # This will now be a short link
            print(f"Thumbnail: {p['thumbnail']}")
        print("-" * 20)
    else:
        print("\nExecution finished. No products retrieved.")