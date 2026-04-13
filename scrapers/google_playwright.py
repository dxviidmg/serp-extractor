from playwright.sync_api import sync_playwright
import time

def scrape_google(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(f"https://www.google.com/search?q={query}")
        time.sleep(1)

        input('Oprime enter cuando el captcha sea desbloqueado')

        # Sponsored results - class sVXRqc with data-pcu for URL
        sponsored = []
        sponsored_links = page.locator('a.sVXRqc').all()
        for link in sponsored_links:
            try:
                title = None
                # Try div with aria-level="3"
                try:
                    div = link.locator('div[aria-level="3"] span').first
                    title = div.inner_text(timeout=1000)
                except:
                    pass
                
                # Try h3
                if not title:
                    try:
                        h3 = link.locator('h3').first
                        title = h3.inner_text(timeout=1000)
                    except:
                        pass
                
                if title:
                    # Get URL from data-pcu attribute (contains actual destination)
                    data_pcu = link.get_attribute('data-pcu')
                    if data_pcu:
                        # Take first URL if multiple
                        url = data_pcu.split(',')[0].strip()
                        url = url.replace('&amp;', '&')
                        if url.startswith('http') and title not in [s['title'] for s in sponsored]:
                            sponsored.append({'title': title, 'url': url})
            except:
                continue

        # Organic results - h3 with class LC20lb inside anchor tags
        organic = []
        organic_links = page.locator('a h3.LC20lb').all()
        for h3 in organic_links:
            try:
                title = h3.inner_text(timeout=3000)
                # Get parent anchor
                anchor = h3.locator('xpath=..')
                href = anchor.get_attribute('href')
                if title and href and href.startswith('http') and '/search?' not in href:
                    href = href.replace('&amp;', '&')
                    if title not in [o['title'] for o in organic]:
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
