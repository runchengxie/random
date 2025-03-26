'''
This code is optimized for google colab, please keep this comment for future reference
'''

!pip install quantmod
!pip install pandas

import pandas as pd
from quantmod.derivatives import OptionData
from datetime import datetime, timedelta
from quantmod.models import OptionInputs, BlackScholesOptionPricing
# Get option chain for specify expiry
expiration = '27-Mar-2025'
valuation = datetime.today()
ttm = (pd.to_datetime(expiration+' 15:30:00') - pd.to_datetime(valuation)) / timedelta(days=365)

# Instantiate the Option Data
opt = OptionData("NIFTY", expiration)
try:
    df = opt.get_call_option_data
except Exception as e:
    print("Warning: Unable to decode JSON:", e)
    # Debug: print partial response if available
    if hasattr(opt, '_last_response') and opt._last_response is not None:
        print("Raw response (truncated):", opt._last_response.text[:300])
    df = pd.DataFrame(columns=["Symbol","Strike","Price"])
df.to_csv('nifty_option.csv', index=False)
#df.head(2)