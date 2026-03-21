"""
This script scrapes EyesOnFlock's API for Flock transparency portals, and combines them with the existing discovered_urls_brave.txt and discovered_urls_google.txt
to create total_urls.txt, a list of all transparency portals found.
"""
import requests

if __name__ == '__main__':
    url = "https://eyesonflock.com/api/v1/data"

    # calling eyesonfock api
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()

    # pull links from json
    links = []
    for i in range(data['summary']['total_portals_found']):
        links.append(data['portals'][i]['portal_url'])
    scraped_num = data['summary']['total_portals_found']

    # combine with existing list
    # brave
    with open("../data/discovered_urls_brave.txt") as f:
        brave_links = 0
        for i in f:
            link = i.replace('\n', '')
            if link not in links and "transparency.flocksafety.com" in link:
                print(link)
                links.append(link)
                brave_links += 1
    with open("../data/discovered_urls_brave_retries.txt") as f:
        for i in f:
            link = i.replace('\n', '')
            if link not in links and "transparency.flocksafety.com" in link:
                print(link)
                links.append(link)
                brave_links += 1
    print("Brave: " + str(brave_links) + " new links\n")

    # google
    with open("../data/discovered_urls_google.txt") as f:
        google_links = 0
        for i in f:
            link = i.replace('\n', '')
            if link not in links and "transparency.flocksafety.com" in link:
                print(link)
                links.append(link)
                google_links += 1
    print("Google: " + str(google_links) + " new links\n")

    # sample_urls
    with open("../data/sample-flock-urls.txt") as f:
        sample_links = 0
        for i in f:
            link = i.replace('\n', '')
            if link not in links and "transparency.flocksafety.com" in link:
                print(link)
                links.append(link)
                sample_links += 1
    print("Sample URLS: " + str(sample_links) + " new links\n")

    with open("../data/total_urls.txt", "w") as f:
        links.sort()
        for i in links:
            f.write(i + "\n")
