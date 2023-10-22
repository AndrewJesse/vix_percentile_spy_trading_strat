import json
import quandl
import matplotlib.pyplot as plt
import pandas as pd  # Importing the pandas library

# Load API key from JSON file
with open("config.json", "r") as file:
    config = json.load(file)
    quandl_api_key = config["quandl_api_key"]

# Set up Quandl API Key
quandl.ApiConfig.api_key = quandl_api_key

# Fetch LBMA Gold Price Data
data = quandl.get("LBMA/GOLD")

# Filter data to only include the last 3 years
end_date = pd.Timestamp.now()  # Current date
start_date = end_date - pd.DateOffset(years=3)
filtered_data = data[start_date:end_date]

# Plotting the filtered data
plt.figure(figsize=(14, 7))
plt.plot(filtered_data["USD (AM)"], label="AM Price")
plt.plot(filtered_data["USD (PM)"], label="PM Price", linestyle="--")
plt.title("LBMA Gold Prices (Last 3 Years)")
plt.xlabel("Date")
plt.ylabel("Price in USD")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
