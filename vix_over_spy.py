import json
import pandas as pd
import matplotlib.pyplot as plt
import requests

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

# Calculate the percentile of each day's VIX value over the entire dataset
vix_data["Percentile"] = vix_data["value"].rank(pct=True) * 100

# Align the two datasets on their dates
aligned_data = pd.concat([sp500_data, vix_data["Percentile"]], axis=1).dropna()

# Calculate Buy and Hold P/L
buy_and_hold_return = (
    (aligned_data["value"].iloc[-1] - aligned_data["value"].iloc[0])
    / aligned_data["value"].iloc[0]
    * 100
)

# Filter out data where VIX is below 50%
blue_dot_data = aligned_data[aligned_data["Percentile"] < 50].copy()

# Calculate daily returns and filter out extreme outliers
blue_dot_data["Daily Returns"] = blue_dot_data["value"].pct_change()
threshold = 3 * blue_dot_data["Daily Returns"].std()
blue_dot_data = blue_dot_data[
    (blue_dot_data["Daily Returns"] < threshold)
    & (blue_dot_data["Daily Returns"] > -threshold)
]

# Calculate cumulative returns for the blue dot strategy
cumulative_blue_dot_returns = (blue_dot_data["Daily Returns"] + 1).cumprod() - 1
blue_dot_return = cumulative_blue_dot_returns.iloc[-1] * 100

# First Plot
plt.figure(figsize=(14, 7))
for date, row in aligned_data.iterrows():
    color = "red" if row["Percentile"] > 50 else "blue"
    plt.plot([date], [row["value"]], marker="o", markersize=1, color=color)

plt.title("S&P 500 with Color Change based on VIX Percentile")
plt.xlabel("Date")
plt.ylabel("S&P 500 Price")
plt.grid(True)

# Add Annotations for P/L
plt.annotate(
    f"Buy and Hold P/L: {buy_and_hold_return:.2f}%",
    (0.02, 0.95),
    xycoords="axes fraction",
    fontsize=10,
    color="green",
)
plt.annotate(
    f"Blue Dots Only P/L: {blue_dot_return:.2f}%",
    (0.02, 0.90),
    xycoords="axes fraction",
    fontsize=10,
    color="blue",
)

plt.tight_layout()
plt.show()

# Second Plot
plt.figure(figsize=(14, 7))
# Plotting against a continuous range for the x-axis
plt.plot(
    range(len(blue_dot_data)),
    cumulative_blue_dot_returns * 100,  # Convert to percentage
    color="blue",
    marker="o",
    markersize=1,
)

# Annotate P/L for Blue Dot Strategy
plt.annotate(
    f"Final P/L: {blue_dot_return:.2f}%",
    (0.05, 0.95),
    xycoords="axes fraction",
    fontsize=10,
    color="blue",
)

plt.title("S&P 500 Blue Dot Strategy Cumulative P/L")
plt.xlabel("Trading Days")
plt.ylabel("P/L (%)")
plt.grid(True)
plt.tight_layout()
plt.show()
