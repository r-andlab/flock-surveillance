import re

INPUT_FILE = "../data/search_terms.txt"
URL_FILE = "../data/discovered_urls.txt"
RESULTS_FILE = "../scripts/logs/full-url-discovery.txt"
TIMEOUT_FILE = "../data/retry_terms.txt"
LOG_FILE = "../data/full-url-discovery-results.txt"

def check_results(file):
    found = set()
    not_found = set()
    timeout = set()
    urls = set()
    count = 0

    with open(file, "r") as f:
        results = f.readlines()

    with open(INPUT_FILE, "r") as fin:
        input = fin.readlines()
    
    # Places with portals
    for line in results:
        line = line.strip().split(":")
        place = line[1].strip()
        status = line[0].strip()
        if status == "NOT FOUND":
            # print(f"{place} is NOT FOUND")
            not_found.add(place)
        elif status == "FOUND":
            # print(f"{place} is FOUND")
            url = line[3]
            if url in urls and place not in found:
                count += 1
                print(line)
                print(f"place: {place}, url: {url}\n")
            urls.add(url)
            found.add(place)
    
    # Places without portals
    for place in input:
        place = place.strip()
        if place not in found and place not in not_found:
            # print(f"{place} not in found or not_found")
            timeout.add(place)
    print(f"Number of URLs: {len(urls)}")
    print(f"Diff between discovered places and discovered URLS: {count}\n")
    return (found, not_found, timeout)


def main():
    found, not_found, timeout= check_results(RESULTS_FILE)
    print()
    print(f"found: {len(found)}")
    print(f"not found: {len(not_found)}")
    print(f"timeout: {len(timeout)}")
    timeout_lines = "\n".join(list(timeout))

    # with open(URL_FILE, "r") as fin:
    #     places = set()
    #     results = fin.readlines()
    #     portals = set()
    #     for line in results:
    #         # new_portals = line.strip().split("https://")
    #         parts = line.strip().split("transparency.flocksafety.com/")
    #         place = ""
    #         if "pd-" in parts[1]:
    #             place = parts[1].split("pd-")
    #         else:
    #             place = place.split("pd")
    #         print(place)
    #         for p in place:
    #             places.add(p)
    #     no_url = found - places
        # print(no_url)

    # with open(URL_FILE, "w") as fout:
    #     fout.write(portals)
        
    with open(TIMEOUT_FILE, "w") as fout:
        fout.write(timeout_lines)

    with open(LOG_FILE, "w") as fout:
        fout.write(f"found: {len(found)}\nnot found: {len(not_found)}\ntimeout: {len(timeout)}")

if __name__ == "__main__":
    main()
