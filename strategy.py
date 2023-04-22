import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt

from yahooquery import Ticker

TICKERS = ["andf.ol", "auss.ol", "asa.ol", "bakka.ol", "giga.ol", "gsf.ol", "king.ol",
           "lsg.ol", "mowi.ol", "nohal.ol", "salm.ol", "statt.ol", "salme.ol"]

# Hyperparameters
strong_buy_threshold = 0.04  # Example threshold for strong buying (4% above mean return)
buy_threshold = 0.02  # Example threshold for buying (2% above mean return)
sell_threshold = -0.02  # Example threshold for selling (2% below mean return)
strong_sell_threshold = -0.04  # Example threshold for strong selling (4% below mean return)

def create_10_day_periods(historical_prices):
    periods = []
    tickers = historical_prices.index.get_level_values(0).unique()
    min_date = historical_prices.index.get_level_values(1).min()
    max_date = historical_prices.index.get_level_values(1).max()

    date_range = pd.date_range(min_date, max_date, freq='10D')

    for start, end in zip(date_range[:-1], date_range[1:]):
        mask = (historical_prices.index.get_level_values(1) >= start) & (historical_prices.index.get_level_values(1) < end)
        period_prices = historical_prices.loc[mask]

        # Check if we have data for all tickers in this period
        if np.all([ticker in period_prices.index.get_level_values(0).unique() for ticker in tickers]):
            periods.append(period_prices)

    return periods


def calculate_relative_returns(historical_prices):
    close_prices = historical_prices.pivot_table(values='close', index='date', columns='symbol')
    
    # Calculate the returns for each stock over the period
    returns = close_prices.iloc[-1].div(close_prices.iloc[0]).subtract(1)

    # Calculate the mean return for all the stocks
    mean_returns = returns.mean()

    # Subtract the mean return from each stock's return
    relative_returns = returns.subtract(mean_returns)

    return relative_returns

def trading_strategy(relative_returns, strong_buy_threshold, buy_threshold, sell_threshold, strong_sell_threshold):
    signals = {}
    for ticker, return_value in relative_returns.items():
        if return_value > strong_buy_threshold:
            signals[ticker] = "strong buy"
        elif return_value > buy_threshold:
            signals[ticker] = "buy"
        elif return_value < strong_sell_threshold:
            signals[ticker] = "strong sell"
        elif return_value < sell_threshold:
            signals[ticker] = "sell"
        else:
            signals[ticker] = "hold"
    return signals


def backtest_strategy(periods, signals_list):
    tickers = periods[0].index.get_level_values(0).unique()
    initial_capital = 10000
    capital_per_stock = initial_capital / len(tickers)

    starting_price = periods[0]
    portfolio = {ticker: capital_per_stock / starting_price.loc[ticker].iloc[-1]['close'] for ticker in tickers}
    capital = 10000
    portfolio_value = {0 : 100}

    n = 1
    for period_prices, signals in zip(periods, signals_list):
        portfolio_value[n] = 0
        portfolio_value[n] = capital
        print("")
        for ticker in tickers:
            print(ticker, signals[ticker])
            current_price = period_prices.loc[ticker].iloc[-1]['close']
            signal = signals[ticker]
            
            portfolio_value[n] += portfolio[ticker] * current_price

            if signal == "strong buy":
                buy_amount = 0.5 * capital
                shares_to_buy = buy_amount / current_price
                portfolio[ticker] += shares_to_buy
                capital -= buy_amount

            elif signal == "buy":
                buy_amount = 0.2 * capital
                shares_to_buy = buy_amount / current_price
                portfolio[ticker] += shares_to_buy
                capital -= buy_amount

            elif signal == "sell":
                sell_amount = 0.5 * portfolio[ticker] * current_price
                shares_to_sell = sell_amount / current_price
                portfolio[ticker] -= shares_to_sell
                capital += sell_amount

            elif signal == "strong sell":
                sell_amount = 0.9 * portfolio[ticker] * current_price
                shares_to_sell = sell_amount / current_price
                portfolio[ticker] -= shares_to_sell
                capital += sell_amount

        portfolio_value[n] /= 200
        print(portfolio_value[n])
        n += 1

    return portfolio, capital, portfolio_value

# Fetch historical price data for the past year
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=365)
tickers = Ticker(f'{" ".join(TICKERS)}', asynchronous=True)
historical_prices = tickers.history(start=start_date, end=end_date)

periods = create_10_day_periods(historical_prices)

# Example usage
signals_list = []
for period_prices in periods:
    relative_returns = calculate_relative_returns(period_prices)
    signals = trading_strategy(relative_returns, strong_buy_threshold, buy_threshold, sell_threshold, strong_sell_threshold)
    signals_list.append(signals)


portfolio, capital, portfolio_value = backtest_strategy(periods, signals_list)

total_value = 0
prices = Ticker(" ".join(TICKERS)).financial_data
for ticker in prices.keys():
    total_value += prices[ticker]["currentPrice"] * portfolio[ticker]
    
print(total_value + capital)

evolution = [portfolio_value[n] for n in range(len(portfolio_value.keys()))]

plt.plot(evolution)
plt.show()