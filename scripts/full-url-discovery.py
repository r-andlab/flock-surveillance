from playwright.sync_api import sync_playwright
from typing import Set
import time
import re

def duckduckgo_search(search_terms) -> Set[str]:
    """
    Searches DuckDuckGo for all transparency portal search terms.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        discovered_urls = set()
        
        for search in search_terms:
            # search DuckDuckGo for flock safety sites
            found = False
            search = search.strip()
            place, state, pd = search.split(",")
            search_query = "site:transparency.flocksafety.com/"
            page.goto(f"https://duckduckgo.com/?q={search_query}")
            
            # wait for page to load
            page.wait_for_load_state('networkidle')
            
            # get all search_terms matching URL pattern
            # todo: modify pattern
            pattern = r'https://transparency\.flocksafety\.com/([a-z0-9\-\_]+)'
            
            # Keep clicking "more results" to get more pages
            # Limit of 100 pages--currently only finding 41 pages
            for _ in range(3):  
                # print(f"Scanning page {page_num + 1}...")
                more_button = page.locator('a.result--more__btn, button:has-text("More results")')
                if more_button.count() > 0:
                    more_button.first.click()
                    time.sleep(2)
                else:
                    print("No more results found.")
                    break
                
            # Get all transparency portal links on the results page
            html = page.content()
            sites = re.findall(pattern, html) #e.g. santa-barbara-pd-ca
            
            # check for corresponding portal
            for site in sites:
                if place in site and state in site and pd in site:
                    url = f'https://transparency.flocksafety.com/{site}'
                    if url not in discovered_urls:
                        discovered_urls.add(url)
                        found = True
                        print(f"Portal for {search} found: {url}")
            if not found:
                print(f"Portal for {search} not found")
                   
        browser.close()
    
    print(f"\n Found {len(search_terms)} search_terms from DuckDuckGo")
    return search_terms

if __name__ == "__main__":
    with open("generated_search_terms.txt", "r") as f:
        searches = f.readlines()

    # repeat scraping exercise due to varying search results
    existing_pages = duckduckgo_search(searches)

    with open("existing-pages.txt", "a") as fout:
        for url in existing_pages:
            fout.write(f"{url}\n")
    print("Wrote search_terms to existing-pages.txt.\n")
