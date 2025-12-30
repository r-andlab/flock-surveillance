from playwright.sync_api import sync_playwright
from typing import Set
import time
import re

LOG_FILE_PATH = "./logs/full-url-discovery-search.txt"
# each session ID will get a unique IP

PROXY = {
    'server': 'brd.superproxy.io:33335',
    'username': f'brd-customer-hl_489430ac-zone-residential_proxy1-session-{0}',
    'password': 'l6y5810wob0y'
}

def duckduckgo_search(search_terms, session_id=0) -> Set[str]:
    """
    Searches DuckDuckGo for all transparency portal search terms.
    """
    discovered_urls = set()

    # enable restarting where we left off in case of interruptions
    with open(LOG_FILE_PATH, "r") as fout:
        num_searches = len(fout.readlines())
        if num_searches > 0:
            start = num_searches - 1
        else:
            start = 0

    # search brave for corresponding flock portal
    with open(LOG_FILE_PATH, "a") as fout:
        with sync_playwright() as p:
            # start chrome browser window with proxy configuration
            browser = p.chromium.launch(headless=False, proxy=PROXY)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
        
            for i in range(start, len(search_terms)):
                # search DuckDuckGo for flock safety sites
                search = search_terms[i]
                found = False
                search = search.strip()
                place, state = search.split(",")

                url = "https://search.brave.com/search?q=site%3Ahttps%3A%2F%2Ftransparency.flocksafety.com%2F+"
                page.goto(f"{url}+{place}+{state}&source=web")
                
                # wait for page to load
                page.wait_for_load_state('domcontentloaded')

                # wait for search results to appear (#results is brave results container)
                page.wait_for_selector('#results', timeout=10000)           
                
                # get all search_terms matching URL pattern
                # do not make less strict or it will grab html data
                pattern = r'https://transparency\.flocksafety\.com/([a-z0-9\-\_]+)'
            
                    
                # Get all transparency portal links on the results page
                html = page.content()
                sites = re.findall(pattern, html) #e.g. santa-barbara-pd-ca
                
                # check for corresponding portal and log results
                for site in sites:
                    if place in site and state in site:
                        url = f'https://transparency.flocksafety.com/{site}'
                        if url not in discovered_urls:
                            discovered_urls.add(url)
                            found = True
                            print(f"FOUND: Portal for {search}: {url}")
                            fout.write(f"FOUND: {search}: {url}\n")
                if not found:
                    print(f"Not found: Portal for {search}")
                    fout.write(f"NOT FOUND: {search}\n")

                # rotate proxies every 40 searches
                if i % 40 == 0:
                    browser.close()
                    session_id += 1
                    PROXY['username'] = f'brd-customer-hl_489430ac-zone-residential_proxy1-session-{session_id}'
                    browser = p.chromium.launch(headless=False, proxy=PROXY)
                    context = browser.new_context(ignore_https_errors=True)
                    page = context.new_page()
                    
            browser.close()
    
    print(f"\n Done! Found {len(search_terms)} search_terms from DuckDuckGo")
    return search_terms

SEARCH_TERM_PATH = "../data/search_terms.txt"

if __name__ == "__main__":
    with open(SEARCH_TERM_PATH, "r") as f:
        searches = f.readlines()
    existing_pages = duckduckgo_search(searches)

    with open("existing-pages.txt", "a") as fout:
        for url in existing_pages:
            fout.write(f"{url}\n")
    print("Wrote search_terms to existing-pages.txt.\n")
