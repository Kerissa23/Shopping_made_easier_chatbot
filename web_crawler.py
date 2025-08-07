# import requests
# from bs4 import BeautifulSoup
# import html2text


# def get_data_from_website(url):
#     """
#     Retrieve text content and metadata from a given URL.

#     Args:
#         url (str): The URL to fetch content from.

#     Returns:
#         tuple: A tuple containing the text content (str) and metadata (dict).
#     """
#     # Get response from the server
#     response = requests.get(url)
#     if response.status_code == 500:
#         print("Server error")
#         return
#     # Parse the HTML content using BeautifulSoup
#     soup = BeautifulSoup(response.content, 'html.parser')

#     # Removing js and css code
#     for script in soup(["script", "style"]):
#         script.extract()

#     # Extract text in markdown format
#     html = str(soup)
#     html2text_instance = html2text.HTML2Text()
#     html2text_instance.images_to_alt = True
#     html2text_instance.body_width = 0
#     html2text_instance.single_line_break = True
#     text = html2text_instance.handle(html)

#     # Extract page metadata
#     try:
#         page_title = soup.title.string.strip()
#     except:
#         page_title = url.path[1:].replace("/", "-")
#     meta_description = soup.find("meta", attrs={"name": "description"})
#     meta_keywords = soup.find("meta", attrs={"name": "keywords"})
#     if meta_description:
#         description = meta_description.get("content")
#     else:
#         description = page_title
#     if meta_keywords:
#         meta_keywords = meta_description.get("content")
#     else:
#         meta_keywords = ""

#     metadata = {'title': page_title,
#                 'url': url,
#                 'description': description,
#                 'keywords': meta_keywords}

#     return text, metadata

#----------------------------------
# import requests
# from bs4 import BeautifulSoup
# import html2text

# def extract_flipkart_data(url):
#     headers = {"User-Agent": "Mozilla/5.0"}
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.content, "html.parser")

#     product_blocks = soup.select("div._1AtVbE")  # Flipkart product containers

#     products = []
#     for block in product_blocks:
#         title = block.select_one("div._4rR01T")  # Mobile titles
#         price = block.select_one("div._30jeq3")
#         link = block.select_one("a._1fQZEK")

#         if title and price and link:
#             full_link = "https://www.flipkart.com" + link['href']
#             products.append({
#                 "title": title.get_text(strip=True),
#                 "price": price.get_text(strip=True),
#                 "link": full_link
#             })

#     if not products:
#         return "No products found.", {}

#     # Convert to plain text
#     text = "\n\n".join([f"{p['title']} - {p['price']}\n{p['link']}" for p in products])

#     metadata = {
#         "source": "flipkart",
#         "url": url,
#         "product_count": len(products)
#     }

#     return text, metadata


# def extract_amazon_data(url):
#     headers = {"User-Agent": "Mozilla/5.0"}
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.content, "html.parser")

#     product_blocks = soup.select("div.s-main-slot div[data-component-type='s-search-result']")

#     products = []
#     for block in product_blocks:
#         title = block.select_one("h2 span")
#         price_whole = block.select_one("span.a-price-whole")
#         link = block.select_one("a.a-link-normal")

#         if title and price_whole and link:
#             full_link = "https://www.amazon.in" + link['href']
#             products.append({
#                 "title": title.get_text(strip=True),
#                 "price": "₹" + price_whole.get_text(strip=True),
#                 "link": full_link
#             })

#     if not products:
#         return "No products found.", {}

#     text = "\n\n".join([f"{p['title']} - {p['price']}\n{p['link']}" for p in products])

#     metadata = {
#         "source": "amazon",
#         "url": url,
#         "product_count": len(products)
#     }

#     return text, metadata


# def get_data_from_website(url: str):
#     """
#     Wrapper function to scrape based on domain.
#     """
#     if "flipkart.com" in url:
#         return extract_flipkart_data(url)
#     elif "amazon.in" in url:
#         return extract_amazon_data(url)
#     else:
#         raise ValueError("Unsupported website: only Flipkart and Amazon supported for now.")
#------------------
import time
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# --- The Final, Undetectable Driver Setup ---
def get_driver():
    """
    Sets up a stealthy, undetectable Selenium WebDriver, forcing the correct
    browser version to match the user's installation.
    """
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument('--headless=new')
    
    # *** THE DEFINITIVE FIX FOR DRIVER INSTABILITY ***
    # We force the driver to use a specific, stable version.
    # If your Chrome is version 138, this ensures a perfect match.
    # If you update Chrome, you may need to change this number.
    driver = uc.Chrome(options=options, version_main=138)
    
    driver.set_page_load_timeout(60) # Increased timeout for slow pages
    return driver

# --- Final, Intelligent Selenium-Based Scrapers ---

def extract_flipkart_data(url: str):
    """
    Final, most robust scraper for Flipkart using a stable driver and selectors.
    """
    print(f"Scraping Flipkart: {url}")
    driver = get_driver()
    products = []
    try:
        driver.get(url)
        
        # A more direct way to close the pop-up
        try:
            close_button = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='✕'] | //button[contains(text(),'✕')]"))
            )
            close_button.click()
            print("Login pop-up found and closed.")
        except TimeoutException:
            print("No login pop-up found, continuing...")

        # *** THE ULTIMATE FLIPKART FIX: NEW SELECTOR & WAIT ***
        # We wait for the body tag to be present, which always exists,
        # and then give the dynamic content time to load with a sleep.
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Flipkart page body loaded. Waiting for dynamic content...")
        time.sleep(10) # A longer, fixed wait for content to render
        
        # Scroll a few times to load all products
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"Scroll {i+1}/3 complete.")
            time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "lxml")
        
        # This selector targets all possible product card layouts
        for item in soup.select('div[data-id]'):
            try:
                title_element = item.select_one('a.s1Q9rs, ._4rR01T, a.IRpwTa')
                price_element = item.select_one('div._30jeq3')
                link_element = item.select_one('a.s1Q9rs, a._1fQZEK, a.IRpwTa')

                if title_element and price_element and link_element:
                    title = title_element.get_text(strip=True)
                    price = re.sub(r'[^\d.]', '', price_element.get_text(strip=True))
                    link = urljoin("https://www.flipkart.com", link_element['href'])
                    products.append(f"Title: {title}\nPrice: Rs. {price}\nLink: {link}")
            except Exception:
                continue
    
    except Exception as e:
        print(f"An error occurred while scraping Flipkart: {e}")
    finally:
        driver.quit()

    if not products:
        return "No products found on Flipkart.", {}
        
    print(f"Successfully processed {len(products)} products from Flipkart.")
    text = "\n\n".join(products)
    metadata = {"source": "flipkart", "url": url, "product_count": len(products)}
    return text, metadata


def extract_myntra_data(url: str, user_query: str):
    """Scrapes Myntra with relevancy check."""
    # This function is working well, but we'll add a final stability check
    print(f"Scraping Myntra: {url}")
    driver = get_driver()
    products = []
    try:
        driver.get(url)
        
        WebDriverWait(driver, 40).until(
            EC.any_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.results-base")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.noResults-container"))
            )
        )
        
        if driver.find_elements(By.CSS_SELECTOR, "div.noResults-container"):
            print("Myntra returned 'No Results Found'.")
            return "No products found on Myntra.", {}

        print("Myntra product container loaded.")
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        first_titles = [item.text.lower() for item in soup.select('li.product-base h3.product-brand, li.product-base h4.product-product')[:5]]
        query_keywords = [word.lower() for word in user_query.split() if len(word) > 2]
        
        match_count = sum(1 for title in first_titles if any(keyword in title for keyword in query_keywords))
        
        if len(first_titles) > 0 and match_count < 2:
            print(f"Myntra results seem irrelevant to the query '{user_query}'. Stopping scrape.")
            return "No relevant products found on Myntra.", {}

        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)

        soup = BeautifulSoup(driver.page_source, 'lxml')
        
        for item in soup.select('li.product-base'):
            try:
                brand = item.select_one('h3.product-brand').text.strip()
                title = item.select_one('h4.product-product').text.strip()
                price_element = item.select_one('span.product-discountedPrice, div.product-price')
                link = item.select_one('a')['href']

                if brand and title and price_element and link:
                    price_text = price_element.text
                    match = re.search(r'Rs\.\s*(\d+)', price_text)
                    price = match.group(1) if match else re.sub(r'[^\d.]', '', price_text)
                    full_link = urljoin("https://www.myntra.com/", link)
                    full_title = f"{brand} {title}"
                    products.append(f"Title: {full_title}\nPrice: Rs. {price}\nLink: {full_link}")
            except Exception:
                continue
    except Exception as e:
        print(f"An error occurred while scraping Myntra: {e}")
    finally:
        driver.quit()

    if not products:
        return "No products found on Myntra.", {}

    print(f"Successfully processed {len(products)} products from Myntra.")
    text = "\n\n".join(products)
    metadata = {"source": "myntra", "url": url, "product_count": len(products)}
    return text, metadata


def extract_snapdeal_data(url: str):
    """Scrapes Snapdeal using Selenium."""
    # This function is working well.
    print(f"Scraping Snapdeal: {url}")
    driver = get_driver()
    products = []
    try:
        driver.get(url)
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.ID, "products")))
        print("Snapdeal product container loaded.")
        
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)
        
        soup = BeautifulSoup(driver.page_source, 'lxml')

        for item in soup.select('div.product-tuple-listing'):
            try:
                title = item.select_one('p.product-title').text.strip()
                price_element = item.select_one('span.product-price')
                link = item.select_one('a.dp-widget-link')['href']

                if title and price_element and link:
                     price = re.sub(r'[^\d.]', '', price_element.text.strip())
                     products.append(f"Title: {title}\nPrice: Rs. {price}\nLink: {link}")
            except Exception:
                continue
    except Exception as e:
        print(f"An error occurred while scraping Snapdeal: {e}")
    finally:
        driver.quit()
        
    if not products:
        return "No products found on Snapdeal.", {}

    print(f"Successfully processed {len(products)} products from Snapdeal.")
    text = "\n\n".join(products)
    metadata = {"source": "snapdeal", "url": url, "product_count": len(products)}
    return text, metadata


# --- Main Wrapper Function ---
def get_data_from_website(url: str, user_query: str):
    """Calls the correct Selenium-based scraper based on the domain."""
    try:
        if "flipkart.com" in url:
            return extract_flipkart_data(url)
        elif "myntra.com" in url:
            return extract_myntra_data(url, user_query)
        elif "snapdeal.com" in url:
            return extract_snapdeal_data(url)
        else:
            print(f"Warning: No parser available for {url}. Skipping.")
            return f"No parser available for {url}", {}
    except Exception as e:
        print(f"A critical error occurred in get_data_from_website for {url}: {e}")
        return f"Failed to scrape {url}", {}