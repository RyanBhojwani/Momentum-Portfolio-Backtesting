# Momentum-Portfolio-Backtesting

## Overview
This project provides a backtesting framework to evaluate the performance of momentum-based portfolio strategies. Using historical stock returns, momentum scores, and market capitalizations, the model selects a portfolio of the highest momentum stocks each period. It then calculates returns, risk, turnover, and other performance metrics under different weighting schemes and rebalance frequencies.

## Features

### Portfolio Selection and Weighting Options
- **Stock Selection**:
  - Top n stocks are chosen based on their 12-1 momentum each period.
  
- **Weighting Schemes**:
  - Equal-weighted
  - Market-cap weighted
  - Market-cap * momentum weighted

### Rebalancing Options
- **Rebalance Frequency**:
  - Monthly
  - Quarterly

### Metrics and Analysis
- **Portfolio Metrics**:
  - Compound Annual Growth Rate (CAGR)
  - Annualized Standard Deviation
  - Portfolio Turnover
  - Sharpe Ratio

## Requirements
- Python 3
- pandas
- numpy

## Installation
```bash
git clone https://github.com/RyanBhojwani/Momentum-Portfolio-Backtesting.git
cd Momentum-Portfolio-Backtesting
```

## Usage
### Prepare Input Data
- Your data files should include:
    - Monthly Returns.csv: Monthly returns of each stock over time
    - Momentums.csv: Momentum scores for each stock at each time point
    - Market Caps.csv: Market capitalization values for each stock at each time point

### Run the Backtest
- To initiate the backtest, run the following command:
```bash
python Momentum Portfolio Backtesting.py
```

## Input Data Format
Examples of these files are provided.

### Monthly Returns.csv
- Columns: Stock Ticker
- Rows: Monthly Return

### Momentums.csv
- Columns: Stock Ticker
- Rows: Momentum calculated at the proper month

### Market Caps.csv
- Columns: Stock Ticker
- Rows: Market Cap from proper month


## Methodology
### Portfolio Construction
- **Stock Selection:** Stocks are ranked by their momentum score, and the top stocks are chosen for the portfolio.
- **Weighting Schemes:**
  - Equal Weighting: All selected stocks are assigned the same weight in the portfolio.
  - Market Cap Weighting: Stocks are weighted by their market capitalization, with larger companies receiving higher weights.
  - Market Cap * Momentum Weighting: Stocks are weighted based on a combination of market cap and momentum scores.
- **Rebalancing:**
  - The portfolio is rebalanced at a specified frequency, such as monthly or quarterly, by re-evaluating the stocks and their weights.
- **Performance Evaluation:**
  - The backtest computes key performance metrics such as:
    - Compound Annual Growth Rate (CAGR): The average annual return over the backtest period.
    - Annualized Standard Deviation: A measure of the portfolio's risk.
    - Portfolio Turnover: The rate at which assets are bought and sold within the portfolio.
    - Sharpe Ratio: A risk-adjusted performance metric.

## Areas for Enhancement
- Additional Momentum Indicators: Incorporate other momentum indicators such as 6 month momentum, quarterly momentum, moving averages, or RSI.
- Optimization: Use optimization techniques to fine-tune the weighting and rebalancing strategy.
- Transaction Costs: Account for transaction costs in the backtest to simulate more realistic results.
- Portfolio Metrics: Implement more portfolio risk metrics, significance testing, or portfolio visualization.
