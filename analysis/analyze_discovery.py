import re

INPUT_FILE = "../data/search_terms.txt"
URL_FILE = "../data/discovered_urls_brave.txt"
LOG_FILE = "../scripts/logs/full-url-discovery-brave.txt"
TIMEOUT_FILE = "../data/retry_terms.txt"
RESULTS_FILE = "../data/full-url-discovery-brave-results.txt"
SAMPLE_URLS = "../data/sample-flock-urls.txt"

# for retries
# INPUT_FILE = "../data/retry_terms.txt"
# URL_FILE = "../data/discovered_urls_brave_retries.txt"
# LOG_FILE = "../scripts/logs/full-url-discovery-brave-retries.txt"
# TIMEOUT_FILE = "../data/retry_terms_2.txt"
# RESULTS_FILE = "../data/full-url-discovery-brave-retries-results.txt"
# SAMPLE_URLS = "../data/sample-flock-urls.txt"

def check_results(file):
    found = set()
    not_found = set()
    timeout = set()
    urls = set()

    with open(file, "r") as f:
        results = f.readlines()

    with open(INPUT_FILE, "r") as fin:
        input = fin.readlines()
    
    # Places with portals
    for line in results:
        line = line.strip().split(":", 2)
        place = line[1].strip()
        status = line[0].strip()
        if status == "NOT FOUND":
            # print(f"{place} is NOT FOUND")
            not_found.add(place)
        elif status == "FOUND":
            # print(f"{place} is FOUND")
            url = line[2].strip()
            urls.add(url)
            found.add(place)
    
    # Places without portals
    for place in input:
        place = place.strip()
        if place not in found and place not in not_found:
            # print(f"{place} not in found or not_found")
            timeout.add(place)
    print(f"Number of URLs: {len(urls)}")
    return (found, not_found, timeout, urls)

def find_duplicate_mappings():
    url_to_places = {}
    
    with open(LOG_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(":")
            if parts[0].strip() == "FOUND":
                place = parts[1].strip()
                url = f"{parts[2].strip()}:{parts[3].strip()}"
                
                if url not in url_to_places:
                    url_to_places[url] = []
                url_to_places[url].append(place)
    
    # Find URLs with multiple places
    duplicates = {url: places for url, places in url_to_places.items() if len(places) > 1}
    
    print(f"URLs with multiple search terms: {len(duplicates)}")
    print(f"Total duplicate mappings: {sum(len(places) - 1 for places in duplicates.values())}\n")
    
    # Show examples
    print("Examples of multiple places mapping to same URL:")
    for url, places in list(duplicates.items())[:10]:
        print(f"\n{url}:")
        for place in places:
            print(f"  - {place}")

def main():
    found, not_found, timeout, urls = check_results(LOG_FILE)
    # TODO: update to be len(found) when future experiments run. substring matching should be fixed
    print(f"found: {len(urls)}")
    print(f"not found: {len(not_found)}")
    print(f"timeout: {len(timeout)}")
    total = len(urls)+ len(not_found) + len(timeout)
    print(f"double mapped: {31665-total}\n")

    # for main experiment, total will be 3 less than len(search_terms) since I added known
    # cases as the beginning for testing (santa-cruz, berkeley, eugene)
    total = len(found)+ len(not_found) + len(timeout)
    print(f"total: {total}")
    timeout_lines = "\n".join(list(timeout))
    
    sample_urls = set()
    with open(SAMPLE_URLS, "r") as fsample:
        url_lines = fsample.readlines()

    for line in url_lines:
        line = line.strip()
        sample_urls.add(line)
    # print(sample_urls)
    print(f"Number of URLs found that are not in sample URLs: {len(urls-sample_urls)}\n")
    print(f"Number of sample URLs found that are not in the set of found URLs: {len(sample_urls-urls)}\n")
        
    with open(TIMEOUT_FILE, "w") as fout:
        fout.write(timeout_lines)

    with open(RESULTS_FILE, "w") as fout:
        fout.write(f"found: {len(found)}\nnot found: {len(not_found)}\ntimeout: {len(timeout)}\ntotal: {total}")

if __name__ == "__main__":
    main()
