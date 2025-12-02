import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import csv
import time
import random

def clean(s):
    return s.strip().lower().replace(" ", "-")


def long_sleep():
    """Long randomized sleep between visits (20–30 sec)."""
    time.sleep(random.uniform(20, 30))


def human_scroll(driver):
    """Simulate human-like scrolling patterns."""
    try:
        height = driver.execute_script("return document.body.scrollHeight")
        if not height or height < 200:
            return

        # scroll 2–4 times with human pacing
        for _ in range(random.randint(2, 4)):
            pos = random.randint(0, height)
            driver.execute_script(f"window.scrollTo(0, {pos});")
            time.sleep(random.uniform(0.4, 1.2))

    except:
        pass


def human_idle(driver):
    """Optional random idle action: tiny movement, tiny scroll, click nothing."""
    try:
        choice = random.randint(1, 4)

        if choice == 1:
            # tiny scroll up/down
            driver.execute_script("window.scrollBy(0, arguments[0]);",
                                  random.randint(-100, 100))

        elif choice == 2:
            # click somewhere harmless (top-left corner)
            driver.execute_script("""
                const e = document.elementFromPoint(5, 5);
                if (e) e.click();
            """)

        elif choice == 3:
            # scroll to top or bottom
            driver.execute_script("window.scrollTo(0, 0);") if random.random() < 0.5 \
                else driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # small pause
        time.sleep(random.uniform(0.3, 1.0))

    except:
        pass


def is_bad_xml(driver):
    """Detect XML errors to avoid false positives."""
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        return ("the specified key does not exist" in body_text)

    except Exception:
        return False



def main():
    CITY_FILE = "./locations.txt"
    urls = set()

    # Build URL list
    with open(CITY_FILE, "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) != 12:
                continue
            _, _, city, _, state, county_name, *_ = row

            if not city or not state or not county_name:
                continue

            city_clean = clean(city)
            state_clean = clean(state)
            county_clean = clean(county_name)

            urls.update([
                f"https://transparency.flocksafety.com/{city_clean}-{state_clean}-pd",
                f"https://transparency.flocksafety.com/{county_clean}-county-pd",
            ])

    urls = list(urls)
    random.shuffle(urls)

    total = len(urls)
    print(f"Testing {total} URLs")

    # Start browser
    driver = uc.Chrome()

    print("Opened browser — solve Cloudflare manually if needed.")
    driver.get("https://transparency.flocksafety.com/coronado-ca-pd")
    time.sleep(8)

    input("Press Enter once the site loads.\n")
    print("Starting checks...\n")

    working = []
    start = time.time()

    for i, url in enumerate(urls, start=1):

        try:
            driver.get(url)
            time.sleep(1)

            # human-like actions
            human_scroll(driver)
            human_idle(driver)

            # XML / error page detection
            if is_bad_xml(driver):
                print(f"[Invalid XML] {url}")
                long_sleep()
                continue

            title = driver.title.lower()
            if "404" in title or "not found" in title:
                print(f"[404] {url}")
                long_sleep()
                continue

            # SUCCESS
            working.append(url)
            print(f"FOUND: {url}")

        except Exception as e:
            print(f"[Error] {url} → {e}")

        # long human sleep
        long_sleep()

        if i % 50 == 0:
            elapsed = (time.time() - start) / 3600
            print(f"\n{i}/{total} processed | {len(working)} found | elapsed {elapsed:.2f}h\n")

    driver.quit()

    # Save results
    with open("working_urls.txt", "w") as f:
        f.write("\n".join(working))

    hours = (time.time() - start) / 3600
    print(f"\nFinished. Found {len(working)} working URLs in {hours:.1f} hours.")


if __name__ == "__main__":
    main()
