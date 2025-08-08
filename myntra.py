import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def get_myntra_data(query):
    """
    Scrapes Myntra for a given query using Selenium to handle dynamic content.

    Args:
        query (str): The product search query.

    Returns:
        list: A list of dictionaries, where each dictionary represents a product.
    """
    # Setup selenium webdriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no browser window)
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = None  # Initialize driver to None
    try:
        # Use webdriver-manager to automatically handle the driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Format the query for Myntra's URL structure
        search_url = f"https://www.myntra.com/{query.replace(' ', '-')}"
        driver.get(search_url)

        # Wait for the product results grid to be loaded
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'results-base')))
        
        # Scroll down to ensure more products are loaded
        driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(3) # Wait for new products to potentially load

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
    except Exception as e:
        print(f"An error occurred during Selenium execution: {e}")
        return []
    finally:
        if driver:
            driver.quit()

    results = []
    # Find all product containers (Myntra uses 'product-base' class for list items)
    product_list = soup.find_all('li', class_='product-base')

    if not product_list:
        print("No specific products found on the page for the given query.")
        return []

    for product in product_list:
        brand_tag = product.find('h3', class_='product-brand')
        description_tag = product.find('h4', class_='product-product')
        price_container = product.find('div', class_='product-price')
        link_tag = product.find('a', href=True)

        brand = brand_tag.text.strip() if brand_tag else ''
        description = description_tag.text.strip() if description_tag else ''
        
        # Extract price - checking for discounted price first
        price_tag = price_container.find('span', class_='product-discountedPrice') if price_container else None
        if not price_tag and price_container:
            # Fallback to the standard price if no discount is found
            price_tag = price_container.find('span')

        price = price_tag.text.strip() if price_tag else 'N/A'
        
        # Construct the full, clickable URL
        link = "https://www.myntra.com/" + link_tag['href'] if link_tag and link_tag.has_attr('href') else 'N/A'
        
        # Extract thumbnail image
        image_tag = product.find('img', class_='img-responsive')
        thumbnail = image_tag['src'] if image_tag and image_tag.has_attr('src') else 'N/A'

        if link != 'N/A': # Only add products with a valid link
            results.append({
                "title": f"{brand} {description}".strip(),
                "price": price,
                "link": link,
                "source": "Myntra",
                "thumbnail": thumbnail
            })

    return results

# Example usage for testing
if __name__ == "__main__":
    # The first time you run this, it will download the correct webdriver
    print("Searching for 't-shirts' on Myntra...")
    products = get_myntra_data("t-shirts")
    if products:
        print(f"\nFound {len(products)} specific products:")
        for p in products[:5]:  # Print first 5 results for brevity
            print(f"  Title: {p['title']}")
            print(f"  Price: {p['price']}")
            print(f"  Link: {p['link']}")
            print("-" * 20)
    else:
        print("Could not retrieve specific products.")