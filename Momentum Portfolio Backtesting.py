import pandas as pd
import numpy as np
from enum import Enum

class RebalancePeriod(Enum):
    MONTHLY = 1
    QUARTERLY = 3

class PortfolioBacktester:
    def __init__(self, returns_file, momentum_file, market_cap_file):
        """Initialize the backtester with data files."""
        self.monthly_returns_df = pd.read_csv(returns_file)
        self.momentum_df = pd.read_csv(momentum_file)
        self.market_cap_df = pd.read_csv(market_cap_file)
        
    def select_top_stocks(self, date_index, n):
        """Select top n stocks based on momentum for given date."""
        month_returns = self.momentum_df.iloc[date_index]
        month_returns = month_returns.drop(month_returns.index[0])
        top_stocks = month_returns.nlargest(n)
        
        return pd.DataFrame({'Stock': top_stocks.index, 'Momentum Factor': top_stocks.values})
    
    
    def calculate_portfolio_weights(self, top_stocks_df, weight_scheme, month_index):
        """Calculate portfolio weights based on selected scheme."""
        if weight_scheme == 'equal':
            return self._equal_weight(top_stocks_df)
        elif weight_scheme == 'market_cap':
            return self._market_cap_weight(top_stocks_df, month_index)
        elif weight_scheme == 'market_cap_momentum':
            return self._market_cap_momentum_weight(top_stocks_df, month_index)
        else:
            raise ValueError("Invalid weight scheme. Choose 'equal', 'market_cap', or 'market_cap_momentum'")
    
    def _equal_weight(self, top_stocks_df):
        """Calculate equal weights for portfolio."""
        weight = 1 / len(top_stocks_df)
        top_stocks_df['Weight'] = weight
        return top_stocks_df
    
    def _market_cap_weight(self, top_stocks_df, month_index):
        """Calculate market cap weighted portfolio."""
        stocks = top_stocks_df['Stock'].tolist()
        market_caps = self.market_cap_df.iloc[month_index][stocks]
        total_market_cap = market_caps.sum()
        
        if total_market_cap == 0:
            top_stocks_df['Weight'] = float('nan')
        else:
            weights = market_caps / total_market_cap
            top_stocks_df['Weight'] = top_stocks_df['Stock'].map(weights)
            
        return top_stocks_df
    
    def _market_cap_momentum_weight(self, top_stocks_df, month_index):
        """Calculate market cap * momentum weighted portfolio."""
        stocks = top_stocks_df['Stock'].tolist()
        market_caps = self.market_cap_df.iloc[month_index][stocks]
        momentum_factors = top_stocks_df.set_index('Stock')['Momentum Factor']
        
        mc_momentum_product = market_caps * momentum_factors
        total_mc_momentum = mc_momentum_product.sum()
        
        if total_mc_momentum == 0:
            top_stocks_df['Weight'] = float('nan')
        else:
            weights = mc_momentum_product / total_mc_momentum
            top_stocks_df['Weight'] = top_stocks_df['Stock'].map(weights)
            
        return top_stocks_df
    
    
    def calculate_turnover(self, current_portfolio, previous_portfolio):
        """Calculate portfolio turnover ratio."""
        if previous_portfolio is None:
            return np.nan
            
        merged_portfolio = pd.merge(current_portfolio[['Stock', 'Weight']], previous_portfolio[['Stock', 'Weight']], on='Stock', how='outer', suffixes=('_current', '_previous'))
        merged_portfolio.fillna(0, inplace=True)
        weight_diff = abs(merged_portfolio['Weight_current'] - merged_portfolio['Weight_previous'])
        
        return weight_diff.sum() / 2
    
    def calculate_portfolio_return(self, portfolio, month):
        """Calculate portfolio return for given month."""
        portfolio_stocks = portfolio['Stock'].values
        portfolio_weights = portfolio['Weight'].values
        month_returns = self.monthly_returns_df.iloc[month][portfolio_stocks]
        return (month_returns * portfolio_weights).sum()
    
    
    def run_backtest(self, num_stocks, weight_scheme, rebalance_period=RebalancePeriod.QUARTERLY, start_month=15, end_month=59):
        """
        Run the portfolio backtest with given parameters.
        
        Parameters:
        -----------
        num_stocks : int
            Number of stocks to include in the portfolio
        weight_scheme : str
            Weighting scheme ('equal', 'market_cap', or 'market_cap_momentum')
        rebalance_period : RebalancePeriod
            RebalancePeriod.MONTHLY or RebalancePeriod.QUARTERLY
        start_month : int
            Starting month index for the backtest
        end_month : int
            Ending month index for the backtest
        """
        monthly_returns = []
        monthly_turnover = []
        previous_portfolio = None
        rebalance_freq = rebalance_period.value
        
        # Determine rebalancing months
        rebalance_months = range(start_month, end_month, rebalance_freq)
        
        for period_start in rebalance_months:
            # Select and weight portfolio at start of period
            top_stocks = self.select_top_stocks(period_start, num_stocks)
            current_portfolio = self.calculate_portfolio_weights(top_stocks, weight_scheme, period_start)
            
            # Calculate returns and turnover for each month until next rebalance
            for month in range(period_start, min(period_start + rebalance_freq, end_month)):
                monthly_return = self.calculate_portfolio_return(current_portfolio, month + 1)
                turnover = self.calculate_turnover(current_portfolio, previous_portfolio)
                
                monthly_returns.append(monthly_return)
                monthly_turnover.append(turnover)
                
                previous_portfolio = current_portfolio.copy()
        
        return self.calculate_metrics(monthly_returns, monthly_turnover)
    
    
    def calculate_metrics(self, monthly_returns, monthly_turnover):
        """Calculate portfolio performance metrics."""
        returns_df = pd.DataFrame(monthly_returns, columns=['Monthly Return'])
        turnover_df = pd.DataFrame(monthly_turnover, columns=['Monthly Turnover'])
        
        # Calculate CAGR
        total_return = (1 + returns_df['Monthly Return']).prod()
        n_years = len(returns_df) / 12
        cagr = total_return ** (1 / n_years) - 1
        
        # Calculate other metrics
        annual_std = returns_df['Monthly Return'].std() * np.sqrt(12)
        annual_turnover = pd.Series(monthly_turnover).mean() * 12
        sharpe_ratio = (cagr - 0.0385) / annual_std
        
        return {'CAGR': cagr, 'Annual Std Dev': annual_std, 'Annual Turnover': annual_turnover, 'Sharpe Ratio': sharpe_ratio, 'Monthly Returns': returns_df, 'Monthly Turnover': turnover_df}

def main():
    """Main function to run the backtester."""
    # Initialize backtester
    backtester = PortfolioBacktester(returns_file='Monthly Returns.csv', momentum_file='Momentums.csv', market_cap_file='Market Caps.csv')
    
    # Example configurations for both monthly and quarterly rebalancing
    configs = [
        {'num_stocks': 30, 'weight_scheme': 'equal', 'rebalance_period': RebalancePeriod.MONTHLY},
        {'num_stocks': 30, 'weight_scheme': 'market_cap', 'rebalance_period': RebalancePeriod.MONTHLY},
        {'num_stocks': 30, 'weight_scheme': 'market_cap_momentum', 'rebalance_period': RebalancePeriod.MONTHLY},
        {'num_stocks': 30, 'weight_scheme': 'equal', 'rebalance_period': RebalancePeriod.QUARTERLY},
        {'num_stocks': 30, 'weight_scheme': 'market_cap', 'rebalance_period': RebalancePeriod.QUARTERLY},
        {'num_stocks': 30, 'weight_scheme': 'market_cap_momentum', 'rebalance_period': RebalancePeriod.QUARTERLY},
        {'num_stocks': 100, 'weight_scheme': 'equal', 'rebalance_period': RebalancePeriod.MONTHLY},
        {'num_stocks': 100, 'weight_scheme': 'market_cap', 'rebalance_period': RebalancePeriod.MONTHLY},
        {'num_stocks': 100, 'weight_scheme': 'market_cap_momentum', 'rebalance_period': RebalancePeriod.MONTHLY},
        {'num_stocks': 100, 'weight_scheme': 'equal', 'rebalance_period': RebalancePeriod.QUARTERLY},
        {'num_stocks': 100, 'weight_scheme': 'market_cap','rebalance_period': RebalancePeriod.QUARTERLY},
        {'num_stocks': 100, 'weight_scheme': 'market_cap_momentum','rebalance_period': RebalancePeriod.QUARTERLY}
    ]
    
    # Run backtest for each configuration
    for config in configs:
        rebalance_str = "monthly" if config['rebalance_period'] == RebalancePeriod.MONTHLY else "quarterly"
        print(f"\nRunning backtest with {config['num_stocks']} stocks, {config['weight_scheme']} weighting, and {rebalance_str} rebalancing:")
        
        results = backtester.run_backtest(**config)
        
        print(f"CAGR: {results['CAGR']:.4f}")
        print(f"Annual Std Dev: {results['Annual Std Dev']:.4f}")
        print(f"Annual Turnover: {results['Annual Turnover']:.4f}")
        print(f"Sharpe Ratio: {results['Sharpe Ratio']:.4f}")

if __name__ == "__main__":
    main()