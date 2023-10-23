import json
from fredapi import Fred
import matplotlib.pyplot as plt

# Global Variables
CONFIG_PATH = "config.json"
WINDOW_SIZE = 50
PERCENTILE_THRESHOLD = 20  # The user can adjust this value

# Load API keys from JSON file
with open(CONFIG_PATH, "r") as file:
    config = json.load(file)
    FRED_API_KEY = config["fred_api_key"]

fred = Fred(api_key=FRED_API_KEY)


def fetch_vix_data():
    return fred.get_series("VIXCLS")


def calculate_vix_percentile(vix_data):
    # Fill gaps using interpolation
    vix_data_filled = vix_data.interpolate(method="linear")
    # Calculate the percentile of each day's VIX value over a rolling window
    return vix_data_filled.rolling(window=WINDOW_SIZE).apply(
        lambda x: (x.rank(pct=True).iloc[-1]) * 100
    )


def plot_vix_percentile(vix_percentile):
    plt.figure(figsize=(14, 7))
    plt.plot(vix_percentile, label=f"VIX {WINDOW_SIZE}-Day Percentile")
    plt.title(f"VIX {WINDOW_SIZE}-Day Percentile")
    plt.xlabel("Date")
    plt.ylabel("Percentile")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Annotate the percentage of time VIX percentile is below PERCENTILE_THRESHOLD
    below_threshold_percent = (
        (vix_percentile < PERCENTILE_THRESHOLD).sum() / len(vix_percentile) * 100
    )
    plt.annotate(
        f"VIX Percentile is below {PERCENTILE_THRESHOLD}% for {below_threshold_percent:.2f}% of the time",
        (0.05, 0.05),
        xycoords="axes fraction",
        fontsize=10,
        color="red",
    )

    plt.show()


if __name__ == "__main__":
    vix_data = fetch_vix_data()
    vix_percentile = calculate_vix_percentile(vix_data)
    plot_vix_percentile(vix_percentile)
