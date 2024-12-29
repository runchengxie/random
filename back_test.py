import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime
import akshare as ak  # For better China market data

class CSI300Backtest:
    def __init__(self, start_date, end_date=None, initial_capital=1000000):
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date) if end_date else pd.Timestamp.now()
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.position = 0
        self.transaction_cost = 0.001
        self.data = pd.DataFrame()

    def get_data(self):
        try:
            # Try getting data from AKShare first (better source for Chinese markets)
            index_data = ak.stock_zh_index_daily(symbol="sh000300")
            index_data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            index_data.set_index('Date', inplace=True)
            index_data.index = pd.to_datetime(index_data.index)
            
        except Exception as e:
            print(f"AKShare data fetch failed, falling back to yfinance: {e}")
            # Fallback to yfinance
            symbols = ['000300.SS', '399300.SZ']  # Try multiple symbols
            for symbol in symbols:
                try:
                    stock = yf.Ticker(symbol)
                    index_data = stock.history(start=self.start_date, end=self.end_date)
                    if not index_data.empty:
                        break
                except Exception:
                    continue
            
            if index_data.empty:
                raise ValueError("Could not fetch data from any source")

        # Filter date range and handle missing data
        self.data = index_data.loc[self.start_date:self.end_date].copy()
        self.data = self.data.resample('D').ffill()  # Fill missing days
        self.data['Returns'] = self.data['Close'].pct_change()
        self.data.dropna(inplace=True)

        # Add basic technical indicators
        self.data['SMA50'] = self.data['Close'].rolling(window=50).mean()
        self.data['SMA200'] = self.data['Close'].rolling(window=200).mean()
        self.data['Volatility'] = self.data['Returns'].rolling(window=20).std()
        
        # Quality check
        if len(self.data) < 200:  # Minimum required for strategy
            raise ValueError("Insufficient data points for analysis")

    def generate_signals(self):
        # Enhanced signal generation with trend confirmation
        self.data['Signal'] = 0
        
        # Basic trend following with volatility filter
        trend_condition = (self.data['SMA50'] > self.data['SMA200'])
        vol_condition = (self.data['Volatility'] < self.data['Volatility'].rolling(window=50).mean())
        
        self.data.loc[trend_condition & vol_condition, 'Signal'] = 1
        self.data['Position'] = self.data['Signal'].diff()

    def run_backtest(self):
        self.get_data()
        self.generate_signals()

        self.data['Portfolio_Value'] = self.initial_capital
        self.data['Cash'] = self.cash
        self.data['Holdings'] = 0.0

        for i in range(1, len(self.data)):
            date = self.data.index[i]
            price = self.data['Close'].iloc[i]
            
            # Handle position changes
            if self.data['Position'].iloc[i] == 1:  # Buy signal
                shares_to_buy = int(self.cash * 0.95 // price)  # Keep some cash reserve
                cost = shares_to_buy * price * (1 + self.transaction_cost)
                if cost <= self.cash:
                    self.position = shares_to_buy
                    self.cash -= cost
            
            elif self.data['Position'].iloc[i] == -1:  # Sell signal
                self.cash += self.position * price * (1 - self.transaction_cost)
                self.position = 0

            # Update portfolio values
            self.data.at[date, 'Holdings'] = self.position * price
            self.data.at[date, 'Cash'] = self.cash
            self.data.at[date, 'Portfolio_Value'] = self.cash + self.position * price

    def get_metrics(self):
        returns = self.data['Portfolio_Value'].pct_change().dropna()
        total_return = (self.data['Portfolio_Value'].iloc[-1] / self.initial_capital) - 1
        annual_return = (1 + total_return) ** (252 / len(self.data)) - 1
        sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std() if returns.std() != 0 else 0
        max_drawdown = (self.data['Portfolio_Value'] / self.data['Portfolio_Value'].cummax() - 1).min()
        
        return {
            'Total Return': f"{total_return:.2%}",
            'Annual Return': f"{annual_return:.2%}",
            'Sharpe Ratio': f"{sharpe_ratio:.2f}",
            'Max Drawdown': f"{max_drawdown:.2%}",
            'Number of Trades': len(self.data[self.data['Position'] != 0])
        }

    def plot_results(self):
        plt.figure(figsize=(15, 8))
        plt.plot(self.data.index, self.data['Portfolio_Value'], 
                label='Strategy Portfolio', linewidth=2)
        
        # Calculate buy & hold performance
        buy_hold = self.initial_capital * (1 + self.data['Returns']).cumprod()
        plt.plot(self.data.index, buy_hold, 
                label='Buy & Hold', alpha=0.7, linewidth=2)
        
        plt.title('CSI300 Backtest Results', fontsize=12)
        plt.xlabel('Date', fontsize=10)
        plt.ylabel('Portfolio Value (CNY)', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=10)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # Use a more reasonable date range
    start_date = '2015-01-01'  # Starting from 2015
    backtest = CSI300Backtest(start_date=start_date)
    
    try:
        backtest.run_backtest()
        metrics = backtest.get_metrics()
        print("\nBacktest Results:")
        for key, value in metrics.items():
            print(f"{key}: {value}")
        backtest.plot_results()
    except Exception as e:
        print(f"Error during backtest: {e}")
