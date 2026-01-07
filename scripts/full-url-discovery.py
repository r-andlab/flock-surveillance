from playwright.sync_api import sync_playwright
from typing import Set
import time
import re

LOG_FILE_PATH = "./logs/full-url-discovery.txt"
OUTPUT_FILE_PATH = "../data/discovered_urls.txt"

PROXY = {
    'server': 'http://brd.superproxy.io:33335',
    'username': f'brd-customer-hl_489430ac-zone-residential_proxy1-session-{time.time()}',
    'password': 'l6y5810wob0y'
}

def brave_search(search_terms, session_id=time.time()) -> Set[str]:
    """
    Searches Brave for all transparency portal search terms.
    """

    # enable restarting where we left off in case of interruptions
    with open(LOG_FILE_PATH, "r") as fout:
        num_searches = len(fout.readlines())
        if num_searches > 0:
            start = num_searches - 1
        else:
            start = 0

    # enable immediate logging of attempts and results
    f_results = open(OUTPUT_FILE_PATH, "a")
    fout = open(LOG_FILE_PATH, "a")

    # search brave for corresponding flock portal
    with sync_playwright() as p:
        # start chrome browser window with proxy configuration
        browser = p.chromium.launch(headless=False, proxy=PROXY)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
    
        for i in range(start, len(search_terms)):
            # search brave for flock safety sites
            search = search_terms[i]
            found = False
            search = search.strip()
            place, state = search.split(",")

            url = "https://search.brave.com/search?q=site%3Ahttps%3A%2F%2Ftransparency.flocksafety.com%2F+"

            # wait for search results to appear (#results is brave results container)
            try:
                page.goto(f"{url}+{place}+{state}&source=web")
                page.wait_for_selector('#results', timeout=3000)
            
            # if selector times out, typically have encountered a captcha.
            # rotate and try again
            except:
                print(f"TIMEOUT: {place}, {state}. Closing browser and restarting...")  
                browser.close()
                PROXY['username'] = f'brd-customer-hl_489430ac-zone-residential_proxy1-session-{time.time()}'
                browser = p.chromium.launch(headless=False, proxy=PROXY)
                context = browser.new_context(ignore_https_errors=True)
                page = context.new_page()
                continue
            
            # get all search_terms matching URL pattern.
            # do not make less strict or it will grab html data
            pattern = r'https://transparency\.flocksafety\.com/([a-z0-9\-\_]+)'
        
                
            # Get all transparency portal links on the results page
            html = page.content()
            sites = re.findall(pattern, html) #e.g. santa-barbara-pd-ca
            
            # check for corresponding portal and log results
            for site in sites:
                if place in site and state in site:
                    url = f'https://transparency.flocksafety.com/{site}'
                    found = True
                    print(f"FOUND: Portal for {search}: {url}")
                    fout.write(f"FOUND: {search}: {url}\n")
                    fout.flush()
                    f_results.write(f"{url}\n")
                    f_results.flush()
            
            # if not found, report and enter in logs
            if not found:
                print(f"Not found: Portal for {search}")
                fout.write(f"NOT FOUND: {search}\n")
                fout.flush()

            # rotate proxies every 5 searches based on timeouts
            if i > 0 and i % 5 == 0:
                browser.close()
                PROXY['username'] = f'brd-customer-hl_489430ac-zone-residential_proxy1-session-{time.time()}'
                browser = p.chromium.launch(headless=False, proxy=PROXY)
                context = browser.new_context(ignore_https_errors=True)
                page = context.new_page()

    # clean up
    browser.close()
    f_results.close()
    fout.close()

    print(f"\n Done! Found {len(f_results.readlines())} search_terms from brave")

SEARCH_TERM_PATH = "../data/search_terms.txt"

if __name__ == "__main__":
    with open(SEARCH_TERM_PATH, "r") as f:
        searches = f.readlines()
    brave_search(searches)
    print("Wrote search_terms to discovered-urls.txt.\n")
