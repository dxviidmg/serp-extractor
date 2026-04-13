from playwright.sync_api import sync_playwright
import time

def scrape_google(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(f"https://www.google.com/search?q={query}")

        input()

        # Sponsored results - links with 'aclk' in href that contain h3
        sponsored = []
        sponsored_links = page.locator('a[href*="aclk"]').all()
        for link in sponsored_links:
            try:
                h3 = link.locator('h3').first
                title = h3.inner_text(timeout=5000)
                href = link.get_attribute('href')
                if title and href and '/search?' not in href:
                    # Decode HTML entities
                    href = href.replace('&amp;', '&')
                    sponsored.append({'title': title, 'url': href})
            except:
                continue

        # Organic results - h3 with class LC20lb inside anchor tags
        organic = []
        organic_links = page.locator('a h3.LC20lb').all()
        for h3 in organic_links:
            try:
                title = h3.inner_text(timeout=5000)
                # Get parent anchor
                anchor = h3.locator('xpath=..')
                href = anchor.get_attribute('href')
                if title and href and href.startswith('http') and '/search?' not in href:
                    href = href.replace('&amp;', '&')
                    organic.append({'title': title, 'url': href})
            except:
                continue

        print("=== Resultados Patrocinados ===")
        for i, item in enumerate(sponsored):
            print(f"{i+1}. {item['title']}")
            print(f"   {item['url']}")

        print("\n=== Resultados Orgánicos ===")
        for i, item in enumerate(organic[:10]):
            print(f"{i+1}. {item['title']}")
            print(f"   {item['url']}")

        browser.close()


if __name__ == "__main__":
    scrape_google("punto de venta")
