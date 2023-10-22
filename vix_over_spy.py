import json
import pandas as pd
import matplotlib.pyplot as plt
import requests

# User-configurable settings
# ==========================
# Define the VIX percentile threshold for the blue dot strategy
VIX_THRESHOLD = 50  # Values below this percentile are considered for blue dot
# Define the lookback period for VIX percentile calculation
LOOKBACK_DAYS = 50
# ==========================

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


## Fetch VIX and S&P 500 data from FRED
vix_data = fetch_fred_data("VIXCLS", fred_api_key)
sp500_data = fetch_fred_data("SP500", fred_api_key)

# Calculate the overall percentile of each day's VIX value over the dataset
vix_data["Percentile"] = vix_data["value"].rank(pct=True) * 100

# Calculate the rolling percentile of each day's VIX value over a 20-day lookback period
vix_data["Rolling Percentile"] = (
    vix_data["value"]
    .rolling(window=LOOKBACK_DAYS)
    .apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1] * 100)
)
# Fill the NaN values in the "Rolling Percentile" column with the overall VIX percentile
vix_data["Rolling Percentile"].fillna(vix_data["Percentile"], inplace=True)


# Align the two datasets on their dates
aligned_data = pd.concat([sp500_data, vix_data["Rolling Percentile"]], axis=1).dropna()

# Calculate Buy and Hold P/L
buy_and_hold_return = (
    (aligned_data["value"].iloc[-1] - aligned_data["value"].iloc[0])
    / aligned_data["value"].iloc[0]
    * 100
)

# Filter out data where VIX is below the VIX_THRESHOLD
blue_dot_data = aligned_data[aligned_data["Rolling Percentile"] < VIX_THRESHOLD].copy()

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

# Plot the entire S&P 500 data as red lines
plt.plot(
    aligned_data.index,
    aligned_data["value"],
    linestyle="-",
    color="red",
)

# Filter out sequences where VIX is below the threshold and overlay them with blue lines
is_below_threshold = aligned_data["Rolling Percentile"] < VIX_THRESHOLD
start_date = None
for date, below in is_below_threshold.items():
    if below and start_date is None:
        start_date = date
    elif not below and start_date:
        plt.plot(
            aligned_data[start_date:date].index,
            aligned_data[start_date:date]["value"],
            marker="o",
            markersize=1,
            color="blue",
            linestyle="-",
        )
        start_date = None

# To handle the case where the last sequence goes till the end of the dataset
if start_date:
    plt.plot(
        aligned_data[start_date:].index,
        aligned_data[start_date:]["value"],
        marker="o",
        markersize=1,
        color="blue",
        linestyle="-",
    )

plt.title("S&P 500 with Color Change based on VIX Percentile")
plt.xlabel("Date")
plt.ylabel("S&P 500 Price")
plt.grid(True)

# ... rest of your code ...


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
