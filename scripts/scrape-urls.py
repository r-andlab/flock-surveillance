from playwright.sync_api import sync_playwright
import csv
import time
import pandas as pd

# def is_bad_xml(driver):
#     """Detect XML errors to avoid false positives."""
#     try:
#         body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
#         return ("the specified key does not exist" in body_text)

#     except Exception:
#         return False


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

def scrape_multiple_sites(urls, output_file='flock-data.csv'):
    """
    Scrapes multiple transparency portals and saves to csv.
    """
    all_data = {}
    
    with sync_playwright() as p:
        # launch browser once for all sites
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for i, url in enumerate(urls[:10]):
            # track status to alert if we get stuck due to Cloudflare protection
            print(f"Scraping {i+1}/{len(urls)}: {url}")
            
            site_data = scrape_flock_data(page, url)
            _, place = url.split("https://transparency.flocksafety.com/")
            
            # associate page data with url in dict
            all_data[place.strip()] = site_data
            
            # polite delay; unsure if still needed.
            # matters less now that we do proxy rotation
            time.sleep(5)
        
        browser.close()
    
    df = pd.DataFrame.from_dict(all_data)
    # print(df)
    df.to_csv(output_file)

if __name__ == "__main__":
    with open('./flock-urls.txt', 'r') as f:
        urls = f.readlines()
    data = scrape_multiple_sites(urls)
