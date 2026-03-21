from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import csv
import time
import pandas as pd
import random

# def is_bad_xml(driver):
#     """Detect XML errors to avoid false positives."""
#     try:
#         body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
#         return ("the specified key does not exist" in body_text)

#     except Exception:
#         return False

PROXY = {
    'server': 'http://brd.superproxy.io:33335',
    'username': f'brd-customer-hl_489430ac-zone-residential_proxy1-session-{time.time()}',
    'password': 'l6y5810wob0y'
}


def scrape_flock_data(page, url):
    """Scrapes data from a transparency portal."""
    try:
        # navigate to url
        page.goto(url, timeout=30000)
        
        # wait for content to load
        page.wait_for_selector('.label', timeout=10000)
        
        # extract all labels and values
        labels = page.locator('.label').all_inner_texts()
        values = page.locator('.value').all_inner_texts()
        
        # combine into dictionary
        fields = {}
        for i, label in enumerate(labels):
            if i < len(values):
                fields[label.strip()] = values[i].strip()
        
        return fields
    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {'url': url, 'error': str(e)}

def scrape_multiple_sites(urls, output_file='../data/flock-data.csv'):
    """
    Scrapes multiple transparency portals and saves to csv.
    """
    all_data = {}
    
    with sync_playwright() as p:
        # launch browser once for all sites
        browser = p.chromium.launch(headless=False, proxy=PROXY)
        context = browser.new_context(
            ignore_https_errors=True,
            user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
        )
        page = context.new_page()
        stealth = Stealth()
        stealth.apply_stealth_sync(page)
        
        for i, url in enumerate(urls):
            # track status to alert if we get stuck due to Cloudflare protection
            print(f"Scraping {i+1}/{len(urls)}: {url}")
            
            site_data = scrape_flock_data(page, url)
            _, place = url.split("https://transparency.flocksafety.com/")
            
            # associate page data with url in dict
            all_data[place.strip()] = site_data
            
            # polite delay; unsure if still needed.
            # matters less now that we do proxy rotation
            if i > 0 and i % 3 == 0:
                print("Rotating proxy")
                context.close()
                browser.close()
                PROXY['username'] = f'brd-customer-hl_489430ac-zone-residential_proxy1-session-{time.time()}'
                browser = p.chromium.launch(headless=False, proxy=PROXY)
                context = browser.new_context(
                    ignore_https_errors=True,
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()
                stealth.apply_stealth_sync(page)

            time.sleep(random.uniform(3, 6))
        
        browser.close()
    
    df = pd.DataFrame.from_dict(all_data)
    # print(df)
    df.to_csv(output_file)

if __name__ == "__main__":
    with open('../data/total_urls.txt', 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    data = scrape_multiple_sites(urls)
