import json
from fredapi import Fred
import matplotlib.pyplot as plt

# Load API keys from JSON file
with open("config.json", "r") as file:
    config = json.load(file)
    fred_api_key = config["fred_api_key"]

# Set up FRED API Key
fred = Fred(api_key=fred_api_key)

# Fetch VIX data from FRED
vix_data = fred.get_series("VIXCLS")

# Calculate the percentile of each day's VIX value over a rolling window of 35 days
vix_percentile = vix_data.rolling(window=35).apply(
    lambda x: (x.rank(pct=True).iloc[-1]) * 100
)
# Fill gaps using interpolation
vix_data_filled = vix_data.interpolate(method="linear")

# Calculate the percentile of each day's VIX value over a rolling window of 35 days
vix_percentile = vix_data_filled.rolling(window=35).apply(
    lambda x: (x.rank(pct=True).iloc[-1]) * 100
)

# Calculate the percentage of time VIX percentile is below 50%
below_50_percent = (vix_percentile < 50).sum() / len(vix_percentile) * 100

# Plotting the percentile data
plt.figure(figsize=(14, 7))
plt.plot(vix_percentile, label="VIX 35-Day Percentile")
plt.title("VIX 35-Day Percentile")
plt.xlabel("Date")
plt.ylabel("Percentile")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Annotate the percentage of time VIX percentile is below 50%
plt.annotate(
    f"VIX Percentile is below 50% for {below_50_percent:.2f}% of the time",
    (0.05, 0.05),
    xycoords="axes fraction",
    fontsize=10,
    color="red",
)

plt.show()
