import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from collections import Counter
import re

SCRAPE_DATA = "../data/flock-data.csv"

def normalize_label(label):
    label = label.strip()

    if label.lower().startswith("organizations granted access"):
        return "Organizations granted access"

    if label.lower().startswith("organizations sharing their data"):
        return "Organizations sharing data"

    return label

def normalize_list_item(item):
    item = str(item).strip().lower()

    # simple punctuation cleanup
    item = item.rstrip(".")
    item = re.sub(r"\s+", " ", item)

    # unify common variants
    if item in ["license plate", "license plates", "rear license plates"]:
        return "license plates"
    if item in ["vehicle", "vehicles", "rear of vehicles", "image of the rear of vehicles"]:
        return "vehicles"
    if item in ["facial recognition", "face recognition"]:
        return "facial recognition"
    if item in ["people", "person"]:
        return "people"
    if item in ["gender"]:
        return "gender"
    if item in ["race"]:
        return "race"
    if item in ["personal identifying information", "personally identifying information"]:
        return "personal identifying information"

    return item

def split_structured_items(text):
    if not isinstance(text, str):
        return []

    parts = re.split(r',\s*(?![^()]*\))', text)
    return [normalize_list_item(p) for p in parts if p.strip()]

def parse_numeric(value):
    if not isinstance(value, str):
        return np.nan

    value = value.strip()
    if not value or value.lower() == "data unavailable":
        return np.nan

    value = value.replace(",", "")
    try:
        return float(value)
    except ValueError:
        return np.nan
    
def analyze_list_field(df, field_name, top_n=15):
    """
    For a structured comma-separated field:
    - count each item
    - compute appearance rate relative to number of non-null portals for that field
    """
    if field_name not in df.index:
        print(f"{field_name} not found.")
        return None

    values = df.loc[field_name].dropna()
    total_portals = len(values)

    counter = Counter()
    for val in values:
        for item in split_structured_items(val):
            counter[item] += 1

    rows = []
    for item, count in counter.most_common(top_n):
        rows.append({
            "item": item,
            "count": count,
            "rate": count / total_portals
        })

    result = pd.DataFrame(rows)
    print(f"\n=== {field_name} ===")
    print(f"Non-null portals: {total_portals}")
    print(result.to_string(index=False))
    return result

def analyze_numeric_field(df, field_name):
    """
    Compute mean for a numeric row field.
    """
    if field_name not in df.index:
        print(f"{field_name} not found.")
        return np.nan

    values = df.loc[field_name].dropna()
    parsed = [parse_numeric(v) for v in values]
    parsed = [v for v in parsed if not np.isnan(v)]

    mean_val = np.mean(parsed) if parsed else np.nan
    total_val = np.sum(parsed) if parsed else np.nan
    print(f"{field_name}: mean = {mean_val:.2f}" if not np.isnan(mean_val) else f"{field_name}: no valid numeric data")
    print(f"{field_name}: total = {total_val:.2f}" if not np.isnan(total_val) else f"{field_name}: no valid numeric data")
    return mean_val

def data_retention(df):
    days = df.loc['Data retention (in days)'].values
    sum = 0
    for item in days:
        if type(item) is str:
            if "days" in item and "infinity" not in item.lower(): # some just say -infinity
                num, string = item.split(" days")
                sum += float(num)
    mean = sum / len(days)
    print(f"Mean days of data retention: {mean}")

df = pd.read_csv(SCRAPE_DATA, index_col=0)
df = df[~df.index.isna()]
df.index = [normalize_label(label) for label in df.index]
df = df.drop(index=['url', 'error'], errors='ignore')
df = df.groupby(df.index).first()
print(f"Number of unique fields: {len(df.index)}")

category_counts = df.count(axis=1).sort_values(ascending=False)
top_cats = category_counts[:20]
print(category_counts[:60])
# What's Detected                     581
# Prohibited Uses                     579
# What's Not Detected                 578
# Acceptable Use Policy               577
# Access Policy                       568
# Hotlist Policy                      561
# Data retention (in days)            552
# Number of LPR and other cameras     535
# Hotlists Alerted On                 532
# Hotlist hits in the last 30 days    528
# Searches in the last 30 days                    491
# Vehicles detected in the last 30 days           444
# Public Search Audit                             184
# Unique vehicles detected in the last 30 days     99

entry_counts = df.count(axis=0).sort_values(ascending=False)
print(f"Median number of fields filled is {entry_counts.median()}")
# print(entry_counts[:5])
# 224    26, ferndale-mi
# 303    19 clinton-ct
# 101    17
# 367    17
# 355    17
# print(df.iloc[224]["place"])
# print(df.iloc[303]["place"])

# new analyses
detected_df = analyze_list_field(df, "What's Detected", top_n=30)
not_detected_df = analyze_list_field(df, "What's Not Detected", top_n=30)
prohibited_df = analyze_list_field(df, "Prohibited Uses", top_n=30)

print("\n=== Numeric Means ===")
analyze_numeric_field(df, "Vehicles detected in the last 30 days")
analyze_numeric_field(df, "Hotlist hits in the last 30 days")
analyze_numeric_field(df, "Searches in the last 30 days")
analyze_numeric_field(df, "Number of LPR and other cameras")
data_retention(df)

plt.style.use('ggplot')
plt.bar(top_cats.index.values, top_cats.values, color = "darkseagreen")
plt.title("Number of Pages with Category")
plt.xticks(rotation=30, ha='right')  # rotate labels diagonally
plt.tight_layout()
plt.show()