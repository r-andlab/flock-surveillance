import pandas as pd
import numpy as np
import matplotlib.pylab as plt

SCRAPE_DATA = "../data/flock-data.csv"

def normalize_label(label):
    label = label.strip()

    if label.lower().startswith("organizations granted access"):
        return "Organizations granted access"

    if label.lower().startswith("organizations sharing their data"):
        return "Organizations sharing data"

    return label

df = pd.read_csv(SCRAPE_DATA, index_col=0)
df = df[~df.index.isna()]
df.index = [normalize_label(label) for label in df.index]
df = df.drop(index=['url', 'error'], errors='ignore')
df = df.groupby(df.index).first()
days = df.loc['Data retention (in days)'].values
sum = 0
for item in days:
    if type(item) is str:
        if "days" in item and "infinity" not in item.lower(): # some just say -infinity
            num, string = item.split(" days")
            sum += float(num)
mean = sum / len(days)
print(f"Mean days of data retention: {mean}")
print(f"Number of unique fields: {len(df.index)}")

category_counts = df.count(axis=1).sort_values(ascending=False)
top_cats = category_counts[:20]
print(category_counts[:24])
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

plt.style.use('ggplot')
plt.bar(top_cats.index.values, top_cats.values, color = "darkseagreen")
plt.title("Number of Pages with Category")
plt.xticks(rotation=30, ha='right')  # rotate labels diagonally
plt.tight_layout()
plt.show()