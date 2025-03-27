'''
This code is optimized for google colab, please keep this comment for future reference
'''

!pip install yfinance
!pip install pandas

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from requests.exceptions import JSONDecodeError
from google.colab import files
from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

# Get option chain for specify expiry
expiration = '2025-03-27'
valuation = datetime.today()
ttm = (pd.to_datetime(expiration+' 15:30:00') - pd.to_datetime(valuation)) / timedelta(days=365)

# Instantiate the Ticker
tickerSymbol = "SPY"
ticker = yf.Ticker(tickerSymbol)
try:
    df_options = ticker.option_chain(expiration).calls
except JSONDecodeError as e:
    print("JSONDecodeError occurred:", e)
    df_options = pd.DataFrame(columns=["Symbol","Strike","Price"])
except Exception as e:
    print("Warning: Unable to decode JSON:", e)
    # Debug: print partial response if available
    if hasattr(ticker, '_last_response') and ticker._last_response is not None:
        print("Raw response (truncated):", ticker._last_response.text[:300])
    df_options = pd.DataFrame(columns=["Symbol","Strike","Price"])
df_options = df_options.rename(columns={"contractSymbol": "Symbol", "strike": "Strike", "lastPrice": "Price"})
df_options.to_csv(f'{tickerSymbol}_option.csv', index=False)
files.download(f'{tickerSymbol}_option.csv')
#df.head(2)