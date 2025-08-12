from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_zepto(query):
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.zeptonow.com/")

    # Wait for search box to appear (up to 15 seconds)
    try:
        search_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Search')]"))
        )
    except:
        print("Search bar not found.")
        driver.quit()
        return []

    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    time.sleep(5)  # wait for results to load

    # Scroll to load more products
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    products = []
    items = driver.find_elements(By.XPATH, "//div[contains(@class, 'ProductCard')]")

    for item in items:
        try:
            title = item.find_element(By.XPATH, ".//h3").text
        except:
            title = None
        
        try:
            price = item.find_element(By.XPATH, ".//span[contains(@class, 'ProductCard_price')]").text
        except:
            price = None
        
        try:
            link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            link = None
        
        try:
            thumbnail = item.find_element(By.TAG_NAME, "img").get_attribute("src")
        except:
            thumbnail = None

        if title:
            products.append({
                "title": title,
                "price": price,
                "link": link,
                "thumbnail": thumbnail
            })

    driver.quit()
    return products

if __name__ == "__main__":
    data = scrape_zepto("milk")
    for p in data:
        print(f"{p['title']} - {p['price']} - {p['link']} - {p['thumbnail']}")
