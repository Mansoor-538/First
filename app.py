import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from pypfopt import EfficientFrontier, risk_models, expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices

# ==========================================
# 1. DOWNLOAD HISTORICAL STOCK DATA
# ==========================================
# Define the tickers in your portfolio
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

print(f"Downloading historical data for: {', '.join(tickers)}")
# Fetch 5 years of daily adjusted closing prices
data = yf.download(tickers, start="2021-01-01", end="2026-01-01")["Adj Close"]

# Drop missing values
data = data.dropna()

# ==========================================
# 2. CALCULATE EXPECTED RETURNS & RISK
# ==========================================
# Calculate annualized expected returns (using historical average)
mu = expected_returns.mean_historical_return(data)

# Calculate the annualized sample covariance matrix
S = risk_models.sample_cov(data)

print("\n--- Expected Annualized Returns ---")
print(mu)

# ==========================================
# 3. OPTIMIZE FOR MAX SHARPE RATIO
# ==========================================
# Initialize the Efficient Frontier object
ef = EfficientFrontier(mu, S)

# Optimize the weights to maximize the Sharpe Ratio (risk-free rate defaults to 2%)
raw_weights = ef.max_sharpe()

# Clean the weights (rounds off small numbers to 0 and rounds others neatly)
cleaned_weights = ef.clean_weights()

print("\n--- Optimal Portfolio Weights ---")
for ticker, weight in cleaned_weights.items():
    print(f"{ticker}: {weight:.2%}")

# Display overall portfolio performance metrics
print("\n--- Expected Portfolio Performance ---")
performance = ef.portfolio_performance(verbose=True)

# ==========================================
# 4. DISCRETE ALLOCATION (Optional)
# ==========================================
# Calculate how many actual shares to buy given a specific budget
portfolio_budget = 100000  # $100,000 USD
latest_prices = get_latest_prices(data)

da = DiscreteAllocation(cleaned_weights, latest_prices, total_portfolio_value=portfolio_budget)
allocation, leftover = da.greedy_portfolio()

print(f"\n--- Discrete Asset Allocation for ${portfolio_budget:,.2f} Budget ---")
for ticker, shares in allocation.items():
    print(f"{ticker}: {shares} shares")
print(f"Funds remaining: ${leftover:.2f}")

# ==========================================
# 5. VISUALIZE WEIGHTS
# ==========================================
pd.Series(cleaned_weights).plot.pie(figsize=(6, 6), autopct="%1.1f%%")
plt.title("Optimal Portfolio Weight Allocation")
plt.ylabel("")
plt.show()
