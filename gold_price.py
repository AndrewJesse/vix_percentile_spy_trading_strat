import json
import quandl
import matplotlib.pyplot as plt
import pandas as pd

# Load API key from JSON file
with open("config.json", "r") as file:
    config = json.load(file)
    quandl_api_key = config["quandl_api_key"]

# Set up Quandl API Key
quandl.ApiConfig.api_key = quandl_api_key

# Fetch LBMA Gold Price Data
data = quandl.get("LBMA/GOLD")

# Filter data to only include the last 3 years
end_date = pd.Timestamp.now()
start_date = end_date - pd.DateOffset(years=10)
filtered_data = data[start_date:end_date]

# Initialize total P/L
total_pl_percentage = 0

# Plotting
plt.figure(figsize=(14, 7))
plt.plot(filtered_data["USD (AM)"], label="AM Price", color="blue")
# plt.plot(filtered_data["USD (PM)"], label="PM Price", linestyle="--", color="cyan")

# Iterate over each year and simulate the trade
for year in range(start_date.year, end_date.year + 1):
    trade_entry_date = pd.Timestamp(year=year, month=1, day=2)
    trade_exit_date = trade_entry_date + pd.DateOffset(months=3)

    # Adjust trade dates to nearest available data points
    if trade_entry_date not in filtered_data.index:
        trade_entry_date = filtered_data.index[filtered_data.index > trade_entry_date][
            0
        ]
    if trade_exit_date not in filtered_data.index:
        trade_exit_date = filtered_data.index[filtered_data.index > trade_exit_date][0]

    # Get the segment of data corresponding to the trade
    trade_data_segment = filtered_data[trade_entry_date:trade_exit_date]["USD (AM)"]

    entry_price = trade_data_segment.iloc[0]
    exit_price = trade_data_segment.iloc[-1]
    pl_percentage = ((exit_price - entry_price) / entry_price) * 100
    total_pl_percentage += pl_percentage

    # Plot the segment corresponding to the trade
    plt.plot(trade_data_segment, color="red")

# Calculate P/L for holding from the start to the end
long_term_entry = filtered_data["USD (AM)"].iloc[0]
long_term_exit = filtered_data["USD (AM)"].iloc[-1]
long_term_pl_percentage = ((long_term_exit - long_term_entry) / long_term_entry) * 100

plt.title("LBMA Gold Prices (Last 3 Years) with Simulated Trades")
plt.xlabel("Date")
plt.ylabel("Price in USD")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Displaying total P/L and long-term P/L
plt.annotate(
    f"Total P/L from Trades: {total_pl_percentage:.2f}%",
    (0.6, 0.05),
    xycoords="axes fraction",
    fontsize=10,
    color="red",
)
plt.annotate(
    f"P/L from Long-Term Holding: {long_term_pl_percentage:.2f}%",
    (0.6, 0.02),
    xycoords="axes fraction",
    fontsize=10,
    color="green",
)

plt.show()
