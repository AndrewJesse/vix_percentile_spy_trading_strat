# VIX Percentile Analysis with S&P 500 Strategy

This project seeks to analyze the VIX percentile and its correlation with the S&P 500 index. The core premise is that by observing the VIX percentile, one can potentially avoid significant drawdowns in their investment or trading account.

The **VIX**, often termed the "fear index", represents the market's expectation of volatility over the next 30 days. Typically, when the S&P 500 (SPY) drops, the VIX tends to rise, signaling increased fear or uncertainty in the market. However, the VIX's raw value alone can sometimes be misleading. Instead, analyzing the VIX's percentile over a defined lookback period can offer a more normalized view of market volatility, making it a potentially more effective tool for decision-making.

By utilizing the VIX percentile, this project implements a trading strategy on the S&P 500, aiming to capitalize on this relationship.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

To run this project, you need to have Python installed along with the following libraries:
- `pandas`
- `matplotlib`
- `requests`
- `fredapi`
- `json`

You can install them using pip:
```bash
pip install pandas matplotlib requests fredapi
```

### Configuration

Before you run the project, you need to:

1. **Clone the Repository**: 
   ```bash
   git clone https://github.com/AndrewJesse/vix_percentile_spy_trading_strat
   ```
   
2. **API Keys Setup**:
   - Create a `config.json` file in the root directory of the project.
   - Obtain API keys from [FRED](https://fred.stlouisfed.org/) and [Quandl](https://www.quandl.com/).
   - Add the keys to the `config.json` file in the following format:
   ```json
   {
       "fred_api_key": "YOUR_FRED_API_KEY",
       "quandl_api_key": "YOUR_QUANDL_API_KEY"
   }
   ```
   **Note**: Make sure not to share or expose your API keys. Always keep the `config.json` file in `.gitignore` if you're pushing to a public repository.

### Adjusting the Strategy

You can fine-tune the strategy by adjusting the global variables in `spy_long_strat.py`. The `VIX_THRESHOLD` and `LOOKBACK_DAYS` are particularly relevant, allowing you to modify the VIX percentile threshold and the lookback period, respectively.

### Running the Project

Navigate to the project directory and run the main Python script:
```bash
python spy_long_strat.py
```

## Contribution

Feel free to fork the project and submit pull requests. All contributions are welcome.

## License

This project is licensed under the MIT License.

---
## The blue lines represent the long position is on
![Results of Trade Strat](https://github.com/AndrewJesse/vix_percentile_spy_trading_strat/assets/53543737/424787a4-0689-4723-b68a-1a93fb21d6d4)

## The P/L from the strategy
![results of strat](https://github.com/AndrewJesse/vix_percentile_spy_trading_strat/assets/53543737/411c8a3c-3889-4f00-b39d-bc297db24659)
