from playwright.sync_api import sync_playwright
import csv
import time
import pandas as pd

def scrape_flock_data(page, url):
    """Scrapes data from a single Flock Safety transparency page."""
    try:
        # Navigate to the page
        page.goto(url, timeout=30000)
        
        # Wait for content to load
        page.wait_for_selector('.label', timeout=10000)
        
        # Extract all labels and values
        labels = page.locator('.label').all_inner_texts()
        values = page.locator('.value').all_inner_texts()
        
        # Combine into dictionary
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
    Scrapes multiple Flock Safety sites and saves to CSV.
    
    Args:
        urls: List of URLs to scrape
        output_file: Output CSV filename
    """
    all_data = {}
    
    with sync_playwright() as p:
        # Launch browser once for all sites
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for i, url in enumerate(urls[:10]):
            print(f"Scraping {i+1}/{len(urls)}: {url}")
            site_data = scrape_flock_data(page, url)
            _, place = url.split("https://transparency.flocksafety.com/")
            all_data[place.strip()] = site_data
            
            # Be polite - add a small delay between requests
            time.sleep(1)
        
        browser.close()
    
    df = pd.DataFrame.from_dict(all_data)
    print(df)
    df.to_csv(output_file)

# Example usage
if __name__ == "__main__":
    with open('./flock-urls.txt', 'r') as f:
        urls = f.readlines()
    data = scrape_multiple_sites(urls)
