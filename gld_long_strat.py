import json
import pandas as pd
import matplotlib.pyplot as plt
import requests
import quandl

# User-configurable settings
VIX_THRESHOLD = 50
LOOKBACK_DAYS = 20

# Load API keys from JSON file
with open("config.json", "r") as file:
    config = json.load(file)
    fred_api_key = config["fred_api_key"]
    quandl_api_key = config["quandl_api_key"]

quandl.ApiConfig.api_key = quandl_api_key


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


# Fetch VIX data from FRED
vix_data = fetch_fred_data("VIXCLS", fred_api_key)

# Fetch LBMA Gold Price Data from Quandl
gold_data = quandl.get("LBMA/GOLD")["USD (AM)"]

# Calculate the VIX percentiles
vix_data["Percentile"] = vix_data["value"].rank(pct=True) * 100
vix_data["Rolling Percentile"] = (
    vix_data["value"]
    .rolling(window=LOOKBACK_DAYS)
    .apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1] * 100)
)
vix_data["Rolling Percentile"].fillna(vix_data["Percentile"], inplace=True)

# Align gold data with VIX data
aligned_data = pd.concat([gold_data, vix_data["Rolling Percentile"]], axis=1).dropna()

# Calculate P/L% for the entire duration
long_term_entry = aligned_data["USD (AM)"].iloc[0]
long_term_exit = aligned_data["USD (AM)"].iloc[-1]
long_term_pl_percentage = ((long_term_exit - long_term_entry) / long_term_entry) * 100

# Calculate P/L% for the strategy
strategy_data = aligned_data[aligned_data["Rolling Percentile"] > VIX_THRESHOLD]
strategy_pl_percentage = (
    (strategy_data["USD (AM)"].iloc[-1] - strategy_data["USD (AM)"].iloc[0])
    / strategy_data["USD (AM)"].iloc[0]
) * 100

# Plotting
plt.figure(figsize=(14, 7))
plt.plot(aligned_data.index, aligned_data["USD (AM)"], linestyle="-", color="red")

is_above_threshold = aligned_data["Rolling Percentile"] > VIX_THRESHOLD
start_date = None
for date, above in is_above_threshold.items():
    if above and start_date is None:
        start_date = date
    elif not above and start_date:
        plt.plot(
            aligned_data[start_date:date].index,
            aligned_data[start_date:date]["USD (AM)"],
            marker="o",
            markersize=1,
            color="blue",
            linestyle="-",
        )
        start_date = None
if start_date:
    plt.plot(
        aligned_data[start_date:].index,
        aligned_data[start_date:]["USD (AM)"],
        marker="o",
        markersize=1,
        color="blue",
        linestyle="-",
    )

# Annotations
plt.annotate(
    f"Total P/L from Strategy: {strategy_pl_percentage:.2f}%",
    (0.02, 0.95),
    xycoords="axes fraction",
    fontsize=10,
    color="blue",
)
plt.annotate(
    f"P/L from Long-Term Holding: {long_term_pl_percentage:.2f}%",
    (0.02, 0.90),
    xycoords="axes fraction",
    fontsize=10,
    color="green",
)

plt.title("Gold Prices with Color Change based on VIX Percentile")
plt.xlabel("Date")
plt.ylabel("Gold Price in USD")
plt.grid(True)
plt.tight_layout()
plt.show()
