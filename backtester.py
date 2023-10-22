import json
import pandas as pd
import requests
import numpy as np

# Load API keys from JSON file
with open("config.json", "r") as file:
    config = json.load(file)
    fred_api_key = config["fred_api_key"]


# Function to get data from FRED
def fetch_fred_data(series_id, api_key):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"
    response = requests.get(url)
    data = response.json()["observations"]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


# Fetch VIX and S&P 500 data from FRED
vix_data = fetch_fred_data("VIXCLS", fred_api_key)
sp500_data = fetch_fred_data("SP500", fred_api_key)

print("Fetched VIX data points:", len(vix_data))
print("Fetched S&P 500 data points:", len(sp500_data))
print("Please wait. This may take a minute or two...")

# Precompute Rolling Ranks for all lookback periods
rolling_ranks = {}
for lookback in range(10, 101):
    rolling_ranks[lookback] = (
        vix_data["value"]
        .rolling(lookback)
        .apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1] * 100)
    )

results = {}
for lookback in range(10, 101):
    for i in range(10, 101):
        date_range = vix_data[rolling_ranks[lookback] < i].index
        sp500_subset = sp500_data[sp500_data.index.isin(date_range)]
        if not sp500_subset.empty:
            pl = (
                (sp500_subset["value"].iloc[-1] - sp500_subset["value"].iloc[0])
                / sp500_subset["value"].iloc[0]
            ) * 100
            results_key = f"Lookback {lookback}, Threshold {i}"
            results[results_key] = pl
            # print(f"{results_key}: {pl:.2f}% P/L")
        else:
            print(f"No data for Lookback {lookback}, Threshold {i}")

# After all results are calculated, sort and print in descending order
sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)

# Display only the top 10 results
print("\nTop 10 Results:")
for key, value in sorted_results[:10]:
    print(f"{key}: {value:.2f}% P/L")
