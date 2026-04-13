from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


def scrape_bing(query):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(f"https://www.bing.com/search?q={query}")
        time.sleep(3)
        
        results = []
        for item in driver.find_elements(By.CSS_SELECTOR, "li.b_algo")[:10]:
            title_elem = item.find_element(By.CSS_SELECTOR, "h2")
            link_elem = item.find_element(By.CSS_SELECTOR, "a")
            results.append({
                "title": title_elem.text,
                "link": link_elem.get_attribute("href")
            })
        
        print(f"Found {len(results)} results")
        return results
    finally:
        driver.quit()


if __name__ == "__main__":
    results = scrape_bing("messi")
    for r in results:
        print(f"\n{r['title']}")
        print(f"  {r['link']}")
