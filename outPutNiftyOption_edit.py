# 判断是否在 Google Colab 环境下运行
try:
    from google.colab import files, drive
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

# 如果在 Colab 环境下，安装必要的包（已安装则会跳过）
if IN_COLAB:
    !pip install yfinance
    !pip install pandas
else:
    print("当前为本地环境，请确保已安装 yfinance 和 pandas。")

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from requests.exceptions import JSONDecodeError

# 如果在 Colab 环境下，挂载 Google Drive
if IN_COLAB:
    drive.mount('/content/drive')
else:
    print("本地环境，不需要挂载 Google Drive。")

# 设置期权到期日期和估值日期
expiration = '2025-03-27'
valuation = datetime.today()
ttm = (pd.to_datetime(expiration + ' 15:30:00') - pd.to_datetime(valuation)) / timedelta(days=365)

# 获取指定标的的期权数据
tickerSymbol = "SPY"
ticker = yf.Ticker(tickerSymbol)

try:
    df_options = ticker.option_chain(expiration).calls
except JSONDecodeError as e:
    print("发生 JSONDecodeError 错误:", e)
    df_options = pd.DataFrame(columns=["Symbol", "Strike", "Price"])
except Exception as e:
    print("警告：无法解码 JSON 数据:", e)
    # 如果可用，打印部分原始响应内容帮助调试
    if hasattr(ticker, '_last_response') and ticker._last_response is not None:
        print("原始响应内容（部分）:", ticker._last_response.text[:300])
    df_options = pd.DataFrame(columns=["Symbol", "Strike", "Price"])

# 重命名列，统一格式
df_options = df_options.rename(columns={"contractSymbol": "Symbol", "strike": "Strike", "lastPrice": "Price"})

# 保存数据为 CSV 文件
filename = f'{tickerSymbol}_option.csv'
df_options.to_csv(filename, index=False)

if IN_COLAB:
    files.download(filename)
else:
    print(f"CSV 文件已保存为 {filename} ，请在当前目录中查找。")
