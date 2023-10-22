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

# Plotting the data
plt.figure(figsize=(14, 7))
plt.plot(vix_data, label="VIX")
plt.title("VIX Index")
plt.xlabel("Date")
plt.ylabel("VIX Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
