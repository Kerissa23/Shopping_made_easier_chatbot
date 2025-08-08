import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def get_snapdeal_data(query):
    """
    Scrapes Snapdeal for a given query using Selenium to get specific product details.

    Args:
        query (str): The product search query.

    Returns:
        list: A list of dictionaries, where each dictionary represents a product.
    """
    # Setup selenium webdriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Navigate to Snapdeal's search page
        search_url = f"https://www.snapdeal.com/search?keyword={query.replace(' ', '%20')}"
        driver.get(search_url)

        # Wait for the main product container to load
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.ID, 'products')))
        
        time.sleep(2)  # Allow a moment for dynamic content to settle

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
    except Exception as e:
        print(f"An error occurred during Selenium execution for Snapdeal: {e}")
        return []
    finally:
        if driver:
            driver.quit()

    results = []
    # Find all product containers. On Snapdeal, each is a 'div' with class 'product-tuple-listing'
    product_list = soup.find_all('div', class_='product-tuple-listing')

    if not product_list:
        print("No specific products found on Snapdeal for the given query.")
        return []

    for product in product_list:
        # Title is in a 'p' tag with class 'product-title'
        title_tag = product.find('p', class_='product-title')
        
        # Price is in a 'span' with class 'product-price'
        price_tag = product.find('span', class_='product-price')
        
        # The link is on the parent 'a' tag
        link_tag = product.find('a', class_='dp-widget-link')

        # Image is often lazy-loaded, so we check for 'data-src' or 'src'
        image_tag = product.find('img', class_='product-image')
        thumbnail = 'N/A'
        if image_tag:
            thumbnail = image_tag.get('data-src') or image_tag.get('src')

        # Only proceed if we have the essential information
        if title_tag and price_tag and link_tag and link_tag.has_attr('href'):
            title = title_tag.get('title', title_tag.text).strip()
            price = price_tag.text.strip()
            link = link_tag['href']
            
            # The link should be a full URL, but we double-check
            if link.startswith('//'):
                link = 'https:' + link
            elif not link.startswith('http'):
                # This case is unlikely but good to handle
                continue

            results.append({
                "title": title,
                "price": price,
                "link": link,
                "source": "Snapdeal",
                "thumbnail": thumbnail
            })

    return results

# Example usage for testing
if __name__ == "__main__":
    print("Searching for 'wireless earphones' on Snapdeal...")
    products = get_snapdeal_data("wireless earphones")
    if products:
        print(f"\nFound {len(products)} specific products on Snapdeal:")
        for p in products[:5]:  # Print first 5 results
            print(f"  Title: {p['title']}")
            print(f"  Price: {p['price']}")
            print(f"  Link: {p['link']}")
            print(f" Thumbnail: {p['thumbnail']}")
            print("-" * 20)
    else:
        print("Could not retrieve specific products from Snapdeal.")