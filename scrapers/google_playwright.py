from playwright.sync_api import sync_playwright
import time
import json
import tldextract

def clean_link(link):
    ext = tldextract.extract(link)
    base_domain = f"{ext.domain}.{ext.suffix}"
    return base_domain

def load_results():
    try:
        with open('results.json', 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_results(results):
    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def scrape_google(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(f"https://www.google.com/search?q={query}")
        time.sleep(1)

        input('Oprime enter cuando el captcha sea desbloqueado')

        results = []

        organic_links = page.locator('a h3.LC20lb').all()
        for h3 in organic_links:
            try:
                title = h3.inner_text(timeout=3000)
                anchor = h3.locator('xpath=..')
                href = anchor.get_attribute('href')
                if title and href and href.startswith('http') and '/search?' not in href:
                    href = href.replace('&amp;', '&')
                    clean = clean_link(href)
                    results.append({'query': query, 'link_original': href, 'link_clean': clean, 'is_organic': True})
            except:
                continue

        sponsored_links = page.locator('a.sVXRqc').all()
        for link in sponsored_links:
            try:
                title = None
                try:
                    div = link.locator('div[aria-level="3"] span').first
                    title = div.inner_text(timeout=1000)
                except:
                    pass
                
                if not title:
                    try:
                        h3 = link.locator('h3').first
                        title = h3.inner_text(timeout=1000)
                    except:
                        pass
                
                if title:
                    data_pcu = link.get_attribute('data-pcu')
                    if data_pcu:
                        url = data_pcu.split(',')[0].strip()
                        url = url.replace('&amp;', '&')
                        if url.startswith('http'):
                            clean = clean_link(url)
                            results.append({'query': query, 'link_original': url, 'link_clean': clean, 'is_organic': False})
            except:
                continue

        browser.close()
        return results


def scrape_multiple(searches):
    all_results = load_results()
    
    for query in searches:
        # Check if query already exists
        existing_queries = [r['query'] for r in all_results]
        if query in existing_queries:
            print(f"Skipping {query} - already scraped")
            continue
        
        print(f"Scraping: {query}")
        results = scrape_google(query)
        all_results.extend(results)
        save_results(all_results)


if __name__ == "__main__":
    with open('searches.txt', 'r', encoding='utf-8') as f:
        searches = [line.strip() for line in f if line.strip()]
    scrape_multiple(searches)
