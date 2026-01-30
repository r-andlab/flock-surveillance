import csv

LINK_FILE = "../data/flock-urls.txt"
CITIES_FILE = "../data/cities/uscities.csv"

def get_cities(file):
    cities = set()
    with open(file, "r") as f:
        city_data = csv.DictReader(f)
        for row in city_data:
            city = row["city"].lower().replace(" ", "-")
            state = row["state_id"].lower()
            location = f"{city}-{state}"
            cities.add(location)
    return cities

def check_links(file, cities):
    with open(file, "r") as f:
        links = f.readlines()

    city = 0
    county = 0
    college = 0
    reservation = 0
    airport = 0
    other = []
    total = len(links)
    
    for line in links:
        line = line.strip()
        if "county" in line:
            county += 1
        elif "college" in line or "university" in line:
            college += 1
        elif "airport" in line:
            airport += 1
        elif "tribal" in line:
            reservation += 1
        else:
            _, name = line.split("https://transparency.flocksafety.com/")
            if "pd" in name:
                name = name.replace("-pd", "")
            if name[-1] == "-":
                name = name[:-1]
            if name in cities:
                city += 1
            else:
                other.append(line)
    return (city, county, college, reservation, airport, other, total)


def main():
    cities = get_cities(CITIES_FILE)
    city, county, college, reservation, airport, other, total = check_links(LINK_FILE, cities)
    # based on manual inspection of other, most are oddly formatted cities/towns
    city += len(other) - 10 # based on manual inspection--definitely change for other data sources.
    other = 10
    print(f"city: {city}")
    print(f"county: {county}")
    print(f"college: {college}")
    print(f"reservation: {reservation}")
    print(f"airport: {airport}")
    print(f"other: {other}")
    print(f"total: {total}")
    # other:
    # https://transparency.flocksafety.com/ncric
    # https://transparency.flocksafety.com/paul-bunyan-task-force-mn
    # https://transparency.flocksafety.com/providence-pd-npd-lpr-study-ri
    # https://transparency.flocksafety.com/ohio-le-flock-training
    # https://transparency.flocksafety.com/flock-safety-marketing
    # https://transparency.flocksafety.com/lakeshore-homes-association-ca-
    # https://transparency.flocksafety.com/flock-safety-admins
    # https://transparency.flocksafety.com/cal-maritime-ca
    # https://transparency.flocksafety.com/flock-safety-sales
    # https://transparency.flocksafety.com/flock-safety-le-training



if __name__ == "__main__":
    main()
