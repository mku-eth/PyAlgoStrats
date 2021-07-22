import yfinance as yf

spy_df = yf.download('SPY', start='2000-01-01')

spy_df.to_csv('spy2000.csv')