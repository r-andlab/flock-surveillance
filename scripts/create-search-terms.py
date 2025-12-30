import csv

def clean(s):
    return s.strip().lower().replace(" ", "-")

def main():
    CITY_FILE = "./locations.txt"
    search_terms = set()

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

            search_terms.update([
                f"{city_clean},{state_clean}",
                f"{county_clean},{state_clean}",
            ])

    # Save results
    with open("generated_search_terms.txt", "w") as f:
        f.write("\n".join(search_terms))
    
    print(f"\nDone. Found {len(search_terms)} working search_terms.")


if __name__ == "__main__":
    main()
