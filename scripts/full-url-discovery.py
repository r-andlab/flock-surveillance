from playwright.sync_api import sync_playwright
from typing import Set
import time
import re

# Remember to change file paths for each experiment!
LOG_FILE_PATH = "./logs/full-url-discovery-google.txt"
OUTPUT_FILE_PATH = "../data/discovered_urls_google.txt"
SEARCH_TERM_PATH = "../data/search_terms.txt"

PROXY = {
    'server': 'http://brd.superproxy.io:33335',
    'username': f'brd-customer-hl_489430ac-zone-residential_proxy1-session-{time.time()}',
    'password': 'l6y5810wob0y'
}

def google_search(search_terms, session_id=time.time()) -> Set[str]:
    """
    Searches Google for all transparency portals based on search terms.
    """
    import random
    
    # restart where we left off in case of interruptions
    with open(LOG_FILE_PATH, "r") as fout:
        num_searches = len(fout.readlines())
        if num_searches > 0:
            start = num_searches - 1
        else:
            start = 0

    # immediately logging attempts and results
    f_results = open(OUTPUT_FILE_PATH, "a")
    fout = open(LOG_FILE_PATH, "a")
    urls = set() # url must be embedded multiple places because it is found 3 times in results;
                # need a set to avoid duplicate logging/output

    # search Google for corresponding flock portal
    with sync_playwright() as p:
        # start chrome browser window with proxy configuration
        browser = p.chromium.launch(headless=False, proxy=PROXY)
        # Google does more aggressive bot checking so we should set a non-botlike user agent
        context = browser.new_context(
            ignore_https_errors=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
    
        for i in range(start, len(search_terms)):
            # search Google for flock safety sites
            place, state = search_terms[i].strip().split(",")
            found = False

            # URL for Google search of form 'site:https://transparency.flocksafety.com/ +eugene+or'
            preface = "https://www.google.com/search?q=site%3Ahttps%3A%2F%2Ftransparency.flocksafety.com%2F"
            url = f"{preface}+%2B{place}%2B{state}"

            # Google uses either #search or #rso for search container
            try:
                page.goto(url)
                page.screenshot(path=f"debug_screenshot_{i}.png")
    
                # PRINT THE PAGE TITLE
                print(f"Page title: {page.title()}")
                
                # PRINT THE URL (in case of redirects)
                print(f"Current URL: {page.url}")
                try:
                    page.wait_for_selector('#search', timeout=3000)
                except:
                    page.wait_for_selector('#rso', timeout=3000)
            
            # if selector times out, likely encountered a captcha.
            # rotate and try again
            except:
                print(f"TIMEOUT: {place}, {state}. Closing browser and restarting...")  
                browser.close()
                PROXY['username'] = f'brd-customer-hl_489430ac-zone-residential_proxy1-session-{time.time()}'
                browser = p.chromium.launch(headless=False, proxy=PROXY)
                context = browser.new_context(
                    ignore_https_errors=True,
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()
                f_out.write(f"TIMEOUT: {place}, {state}.\n")
                continue
            
            # get all search_terms matching URL pattern.
            # do not make less strict or it will grab html data
            pattern = r'https://transparency\.flocksafety\.com/([a-z0-9\-\_]+)'
                
            # Get all transparency portal links on the results page
            html = page.content()
            sites = re.findall(pattern, html) #e.g. santa-barbara-pd-ca
            
            # check for corresponding portal and log results
            for site in sites:
                if f"{place}-" in site and f"-{state}" in site: # always a dash separating place and state
                    url = f'https://transparency.flocksafety.com/{site}'
                    if url not in urls:
                        print(url)
                        urls.add(url) # avoid duplicate logging
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

            # rotate proxies every 3 searches, more frequently than Brave bc Google is stricter
            if i > 0 and i % 3 == 0:
                browser.close()
                PROXY['username'] = f'brd-customer-hl_489430ac-zone-residential_proxy1-session-{time.time()}'
                browser = p.chromium.launch(headless=False, proxy=PROXY)
                context = browser.new_context(
                    ignore_https_errors=True,
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()

    # clean up
    f_results.close()
    fout.close()

    print(f"\n Done!\n")

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
    urls = set() # avoid duplicate logging

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
                f_results.write(f"TIMEOUT: {place}, {state}.\n")
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
                    if url not in urls:
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

            # rotate proxies every 3 searches based on timeouts
            if i > 0 and i % 3 == 0:
                browser.close()
                PROXY['username'] = f'brd-customer-hl_489430ac-zone-residential_proxy1-session-{time.time()}'
                browser = p.chromium.launch(headless=False, proxy=PROXY)
                context = browser.new_context(ignore_https_errors=True)
                page = context.new_page()

    # clean up
    f_results.close()
    fout.close()

    print(f"\n Done!\n")

if __name__ == "__main__":
    with open(SEARCH_TERM_PATH, "r") as f:
        searches = f.readlines()
    google_search(searches)
