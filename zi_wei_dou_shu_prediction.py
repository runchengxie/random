import datetime
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import os

def predict_buy_sell_zi_wei_stock():
    token = os.getenv("TUSHARE_API_KEY")
    if token:
        ts.set_token(token)
        pro = ts.pro_api()
        end_date = datetime.datetime.now().strftime("%Y%m%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y%m%d")

        df = pro.daily(ts_code='600036.SH', start_date=start_date, end_date=end_date)
        df.sort_values('trade_date', inplace=True)
        df.reset_index(drop=True, inplace=True)
    else:
        import akshare as ak
        df = ak.stock_zh_a_daily(symbol="sh600036", adjust="qfq")
        df.rename(columns={"date": "trade_date"}, inplace=True)
        df.sort_values("trade_date", inplace=True)
        df.reset_index(drop=True, inplace=True)
    
    # Convert trade_date to datetime object for better x-axis handling
    df['trade_date'] = pd.to_datetime(df['trade_date'])

    signals = []
    for i in range(len(df)):
        # 以下仅为示例占位逻辑，请替换为紫微斗数相关策略
        if i % 10 == 0:
            signals.append('buy')
        elif i % 15 == 0:
            signals.append('sell')
        else:
            signals.append('hold')

    df['signal'] = signals

    capital = 10000
    holding = False
    shares = 0
    for i in range(len(df)):
        if df.loc[i, 'signal'] == 'buy' and not holding:
            shares = capital // df.loc[i, 'open']
            capital -= shares * df.loc[i, 'open']
            holding = True
        elif df.loc[i, 'signal'] == 'sell' and holding:
            capital += shares * df.loc[i, 'open']
            shares = 0
            holding = False
    if holding:
        capital += shares * df.loc[len(df)-1, 'open']

    roi = (capital - 10000) / 10000 * 100

    plt.figure(figsize=(10,5))
    plt.plot(df['trade_date'], df['close'], label='Close Price')
    buy_points = df[df.signal=='buy']
    sell_points = df[df.signal=='sell']
    # 修改散点图使用日期列作为 x 轴
    plt.scatter(buy_points['trade_date'], buy_points['close'], marker='^', color='g', label='Buy')
    plt.scatter(sell_points['trade_date'], sell_points['close'], marker='v', color='r', label='Sell')
    plt.legend()
    plt.title(f"600036 Stock Trading with Zi Wei Dou Shu Strategy (ROI: {roi:.2f}%)")
    
    # Optimize x-axis tick formatting
    import matplotlib.dates as mdates
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.gcf().autofmt_xdate()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    predict_buy_sell_zi_wei_stock()
