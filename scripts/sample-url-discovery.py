from playwright.sync_api import sync_playwright
from typing import Set
import time
import re

def duckduckgo_search(urls) -> Set[str]:
    """
    Searches DuckDuckGo for all transparency portal URLs.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # search DuckDuckGo for flock safety sites
        search_query = "site:transparency.flocksafety.com"
        page.goto(f"https://duckduckgo.com/?q={search_query}")
        
        # wait for page to load
        page.wait_for_load_state('networkidle')
        
        # get all URls matching URL pattern
        pattern = r'https://transparency\.flocksafety\.com/([a-z\-]+)'
        
        # Keep clicking "more results" to get more pages
        # Limit of 100 pages--currently only finding 41 pages
        for _ in range(100):  
            # print(f"Scanning page {page_num + 1}...")
            
            # Get all links on the page
            html = page.content()
            matches = re.findall(pattern, html)
            
            # filter out page formatting/design/logistics
            for match in matches:
                if match not in ['fonts', 'assets', 'static', 'cdn']:
                    url = f'https://transparency.flocksafety.com/{match}'
                    if url not in urls:
                        urls.add(url)
                        # print(f"\tFound: {url}")
            
            # try to click "more results" button
            try:
                more_button = page.locator('a.result--more__btn, button:has-text("More results")')
                if more_button.count() > 0:
                    more_button.first.click()
                    time.sleep(2)
                else:
                    print("No 'More results' button found")
                    break
            except Exception as e:
                print(f"Could not load more results: {e}")
                break
        
        browser.close()
    
    print(f"\n Found {len(urls)} URLs from DuckDuckGo")
    return urls

if __name__ == "__main__":
    all_urls = set()
    same = False

    # repeat scraping exercise due to varying search results
    for i in range(5):
        print(f"\nSearching DuckDuckGo, Round {i+1}:")
        curr_urls = duckduckgo_search(all_urls)
        all_urls = curr_urls

        # if no new urls twice in a row, break
        if (len(all_urls)== len(curr_urls)) and same:
            break
        if len(all_urls) == len(curr_urls):
            same = True

    with open("../data/sample-flock-urls.txt", "a") as fout:
        for url in all_urls:
            fout.write(f"{url}\n")
    print("Wrote URLs to sample-flock-urls.txt.\n")
