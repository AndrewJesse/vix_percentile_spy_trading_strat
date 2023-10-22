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

# After fetching the data and before any calculations
vix_data = vix_data.resample("B").ffill()
sp500_data = sp500_data.resample("B").ffill()

# Calculate the percentile of each day's VIX value over a rolling window of 35 days
vix_data["Percentile"] = (
    vix_data["value"]
    .rolling(window=35)
    .apply(lambda x: (x.rank(pct=True).iloc[-1]) * 100)
)

# Create trading signals
vix_data["Signal"] = 0
vix_data.loc[
    vix_data["Percentile"] < 50, "Signal"
] = 1  # Going long when VIX percentile is below 50%
vix_data["Position"] = vix_data["Signal"].diff()

# Align dates of VIX and S&P 500
aligned_data = sp500_data.join(vix_data[["Signal"]])

# Calculate P/L for simulated trades and long-term holding
aligned_data["Daily Returns"] = aligned_data["value"].pct_change()
aligned_data["Strategy Returns"] = (
    aligned_data["Signal"].shift(1) * aligned_data["Daily Returns"]
)
cumulative_strategy_returns = (aligned_data["Strategy Returns"] + 1).cumprod()
cumulative_market_returns = (aligned_data["Daily Returns"] + 1).cumprod()
total_strategy_return = cumulative_strategy_returns.iloc[-1] - 1
total_market_return = cumulative_market_returns.iloc[-1] - 1

# ... [rest of the code before plotting]

# Calculate the percentage of days the trade is on
trade_on_percentage = vix_data["Signal"].sum() / len(vix_data) * 100

# Plotting
plt.figure(figsize=(14, 7))
plt.plot(aligned_data["value"], label="S&P 500", color="blue")

# Plotting red segments for active trades
start_date = None
for date, row in aligned_data.iterrows():
    if row["Signal"] == 1 and start_date is None:
        start_date = date
    elif row["Signal"] == 0 and start_date is not None:
        plt.plot(aligned_data[start_date:date]["value"], color="red")
        start_date = None

# If the last trade is still active at the end of the dataset
if start_date is not None:
    plt.plot(aligned_data[start_date:]["value"], color="red", label="Long Position")

plt.title("S&P 500 Price History with Simulated Trades based on VIX Percentile")
plt.xlabel("Date")
plt.ylabel("S&P 500 Price")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Displaying total P/L, long-term P/L, and trade on percentage
plt.annotate(
    f"P/L from Strategy: {total_strategy_return*100:.2f}%",
    (0.6, 0.05),
    xycoords="axes fraction",
    fontsize=10,
    color="red",
)
plt.annotate(
    f"P/L from Holding: {total_market_return*100:.2f}%",
    (0.6, 0.02),
    xycoords="axes fraction",
    fontsize=10,
    color="green",
)
plt.annotate(
    f"Trade is on for {trade_on_percentage:.2f}% of the time.",
    (0.6, -0.01),  # Adjusted the position to avoid overlap
    xycoords="axes fraction",
    fontsize=10,
    color="green",  # Color set to green as per your request
)

plt.show()
percentage_days_trade_on = (vix_data["Signal"].sum() / len(vix_data)) * 100
print(f"Trade is on for {percentage_days_trade_on:.2f}% of the time.")
