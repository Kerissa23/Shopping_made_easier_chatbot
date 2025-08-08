import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_flipkart_data(query):
    """
    Scrapes Flipkart for a given query using Selenium to get specific product details.

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
        
        # Navigate to Flipkart's search page
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        driver.get(search_url)

        # Wait for the main product container to load
        # Flipkart's layout can vary, so we target a common container class '_1YokD2'
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, '_1YokD2')))
        
        time.sleep(2) # Allow a moment for dynamic content to settle

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
    except Exception as e:
        print(f"An error occurred during Selenium execution for Flipkart: {e}")
        return []
    finally:
        if driver:
            driver.quit()

    results = []
    # Flipkart has different classes for grid and list view. We'll try to catch the most common ones.
    # The '_1AtVbE' class usually holds the list of products.
    product_list = soup.find_all('div', class_='_1AtVbE')
    
    # If the above class doesn't work, let's try another common container for each product.
    if not product_list:
        product_list = soup.find_all('div', {'class': '_4ddWXP'}) # For list view items
    if not product_list:
         product_list = soup.find_all('div', {'class': '_2kHMtA'}) # For grid view items

    if not product_list:
        print("No specific products found on Flipkart for the given query.")
        return []

    base_url = "https://www.flipkart.com"

    for product in product_list:
        # Product title is often in a div with class '_4rR01T'
        title_tag = product.find('div', class_='_4rR01T')
        if not title_tag:
            title_tag = product.find('a', class_='s1Q9rs') # Fallback for different view

        # Price is in a div with class '_30jeq3'
        price_tag = product.find('div', class_='_30jeq3')
        
        # The link is on an 'a' tag, often with class '_1fQZEK'
        link_tag = product.find('a', class_='_1fQZEK')
        if not link_tag:
             link_tag = product.find('a', class_='_2UzuFA') # Fallback

        # Image is in an 'img' tag with class '_396cs4'
        image_tag = product.find('img', class_='_396cs4')

        # Only proceed if we have the essential information
        if title_tag and price_tag and link_tag and link_tag.has_attr('href'):
            title = title_tag.text.strip()
            price = price_tag.text.strip()
            # The URL is relative, so we join it with the base URL
            link = urljoin(base_url, link_tag['href'])
            thumbnail = image_tag['src'] if image_tag and image_tag.has_attr('src') else 'N/A'

            results.append({
                "title": title,
                "price": price,
                "link": link,
                "source": "Flipkart",
                "thumbnail": thumbnail
            })

    return results

# Example usage for testing
if __name__ == "__main__":
    print("Searching for 'redmi phone' on Flipkart...")
    products = get_flipkart_data("redmi phone")
    if products:
        print(f"\nFound {len(products)} specific products on Flipkart:")
        for p in products[:5]:  # Print first 5 results
            print(f"  Title: {p['title']}")
            print(f"  Price: {p['price']}")
            print(f"  Link: {p['link']}")
            print("-" * 20)
    else:
        print("Could not retrieve specific products from Flipkart.")