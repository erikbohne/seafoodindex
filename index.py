from yahooquery import Ticker
import pandas as pd
import matplotlib.pyplot as plt
import datetime

TICKERS = ["andf.ol", "auss.ol", "asa.ol", "bakka.ol", "giga.ol", "gsf.ol", "king.ol",
           "lsg.ol", "mowi.ol", "nohal.ol", "salm.ol", "statt.ol", "salme.ol"]

tickers = Ticker(f'{" ".join(TICKERS)}', asynchronous=True)
price_df = tickers.financial_data
stats_df = tickers.key_stats

market_caps = {}

for ticker in price_df.keys():
    market_cap = price_df[ticker]["currentPrice"] * stats_df[ticker]["sharesOutstanding"]
    market_caps[ticker] = market_cap
    
# Sort the market_caps dictionary by values in descending order and select the top 5
sorted_market_caps = dict(sorted(market_caps.items(), key=lambda x: x[1], reverse=True))
    
# Plotting the bar graph
plt.figure(figsize=(12, 6))
plt.bar(sorted_market_caps.keys(), sorted_market_caps.values())
plt.xlabel('Company Ticker')
plt.ylabel('Market Cap')
plt.title('Market Cap for Each Company')
plt.xticks(rotation=45)
plt.show()


# Calculate the end date as today
end_date = datetime.date.today()

# Calculate the start date as one year before the end date
start_date = end_date - datetime.timedelta(days=365)

# Fetch historical price data for the past year
historical_prices = tickers.history(start=start_date, end=end_date)

plt.figure(figsize=(12, 6))

combined_market_cap = None

for ticker in sorted_market_caps.keys():
    ticker_historical_prices = historical_prices.loc[ticker]
    
    # Calculate the market cap for each date
    ticker_historical_prices["Market Cap"] = ticker_historical_prices["close"] * stats_df[ticker]["sharesOutstanding"]

    # Plot the individual market cap evolution for the current company
    plt.plot(ticker_historical_prices.index, ticker_historical_prices["Market Cap"], label=ticker)

    if combined_market_cap is None:
        combined_market_cap = ticker_historical_prices["Market Cap"]
    else:
        combined_market_cap += ticker_historical_prices["Market Cap"]

# Plot the combined market cap evolution for the top 5 companies
plt.plot(combined_market_cap.index, combined_market_cap, label="Combined Market Cap", linewidth=2)

plt.xlabel("Date")
plt.ylabel("Market Cap")
plt.title("Market Cap Evolution for Top 5 Companies and Combined Market Cap (Past Year)")
plt.legend()
plt.show()




