import datetime
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import os

def zi_wei_dou_shu_signal(trade_date):
    """
    基于紫微斗数的思想，使用交易日期的月份和日期模拟星位的吉凶判断：
      - 假设1、4、7、10月为吉月，偶数日视为买入信号
      - 假设2、5、8、11月为凶月，能被3整除的日子视为卖出信号
      - 其它情况保持观望（hold）
    """
    month = trade_date.month
    day = trade_date.day
    if month in [1, 4, 7, 10]:
        if day % 2 == 0:
            return "buy"
        else:
            return "hold"
    elif month in [2, 5, 8, 11]:
        if day % 3 == 0:
            return "sell"
        else:
            return "hold"
    else:
        return "hold"

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
    
    # 将 trade_date 转换为 datetime 类型，便于后续处理
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    
    # 基于紫微斗数思想生成交易信号
    signals = []
    for i in range(len(df)):
        date = df.loc[i, 'trade_date']
        signal = zi_wei_dou_shu_signal(date)
        signals.append(signal)
    df['signal'] = signals

    # 简单回测：初始资金 10000
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
    plt.scatter(buy_points['trade_date'], buy_points['close'], marker='^', color='g', label='Buy')
    plt.scatter(sell_points['trade_date'], sell_points['close'], marker='v', color='r', label='Sell')
    plt.legend()
    plt.title(f"600036 Stock Trading with Zi Wei Dou Shu Strategy (ROI: {roi:.2f}%)")
    
    # 优化 x 轴的日期显示
    import matplotlib.dates as mdates
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.gcf().autofmt_xdate()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    predict_buy_sell_zi_wei_stock()
