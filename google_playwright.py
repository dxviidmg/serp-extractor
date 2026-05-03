from playwright.sync_api import sync_playwright, TimeoutError
import time
import json
import tldextract
from pathlib import Path
from typing import Optional


def clean_link(link: str) -> str:
    """Extract base domain from URL."""
    ext = tldextract.extract(link)
    return f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain


def load_results(filepath: str = "results.json") -> list:
    """Load results from JSON file."""
    path = Path(filepath)
    if not path.exists():
        return []
    try:
        content = path.read_text(encoding='utf-8').strip()
        return json.loads(content) if content else []
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not load {filepath}: {e}")
        return []


def save_results(results: list, filepath: str = "results.json") -> None:
    """Save results to JSON file."""
    Path(filepath).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')


def get_existing_queries(results: list) -> set:
    """Get set of already scraped queries for fast lookup."""
    return {r['query'] for r in results}


def scrape_google(query: str, timeout: int = 10000) -> list:
    """Scrape Google SERP for a single query."""
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            page.goto(f"https://www.google.com/search?q={query}", timeout=timeout)
            page.wait_for_load_state("networkidle", timeout=timeout)
            time.sleep(1)
            
            input('Oprime enter cuando el captcha sea desbloqueado')
            
            # Scrape organic results
            organic_links = page.locator('a h3.LC20lb').all()
            for h3 in organic_links:
                try:
                    title = h3.inner_text(timeout=3000)
                    anchor = h3.locator('xpath=..')
                    href = anchor.get_attribute('href')
                    
                    if title and href and href.startswith('http') and '/search?' not in href:
                        href = href.replace('&amp;', '&')
                        results.append({
                            'query': query,
                            'link_original': href,
                            'link_clean': clean_link(href),
                            'is_organic': True
                        })
                except TimeoutError:
                    continue
                except Exception:
                    continue
            
            # Scrape sponsored results
            sponsored_links = page.locator('a.sVXRqc').all()
            for link in sponsored_links:
                try:
                    title = None
                    
                    # Try div with aria-level="3"
                    try:
                        div = link.locator('div[aria-level="3"] span').first
                        title = div.inner_text(timeout=1000)
                    except TimeoutError:
                        pass
                    
                    # Try h3
                    if not title:
                        try:
                            h3 = link.locator('h3').first
                            title = h3.inner_text(timeout=1000)
                        except TimeoutError:
                            pass
                    
                    if title:
                        data_pcu = link.get_attribute('data-pcu')
                        if data_pcu:
                            url = data_pcu.split(',')[0].strip()
                            url = url.replace('&amp;', '&')
                            if url.startswith('http'):
                                results.append({
                                    'query': query,
                                    'link_original': url,
                                    'link_clean': clean_link(url),
                                    'is_organic': False
                                })
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Error scraping {query}: {e}")
        finally:
            browser.close()
    
    return results


def scrape_multiple(searches: list, filepath: str = "results.json") -> None:
    """Scrape multiple queries, skipping already scraped ones."""
    all_results = load_results(filepath)
    existing_queries = get_existing_queries(all_results)
    
    for query in searches:
        if not query:
            continue
            
        if query in existing_queries:
            print(f"✓ Skipping '{query}' - already scraped")
            continue
        
        print(f"🔍 Scraping '{query}'...")
        results = scrape_google(query)
        
        if results:
            all_results.extend(results)
            existing_queries.add(query)
            save_results(all_results, filepath)
            print(f"  ✓ Added {len(results)} results")
        else:
            print(f"  ⚠ No results found for '{query}'")


def main():
    """Main entry point."""
    searches_file = Path("searches.txt")
    
    if not searches_file.exists():
        print("Error: searches.txt not found")
        return
    
    with open(searches_file, 'r', encoding='utf-8') as f:
        searches = [line.strip() for line in f if line.strip()]
    
    if not searches:
        print("Error: searches.txt is empty")
        return
    
    print(f"Starting scrape for {len(searches)} queries...")
    scrape_multiple(searches)
    print("Done!")


if __name__ == "__main__":
    main()
