import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

def calculate_and_plot_csi300_return():
    # Step 1: 获取CSI 300的历史数据
    # CSI 300的ETF代码是'510300.SS'
    csi300 = yf.Ticker("510300.SS")
    
    # 获取最大可用的历史数据
    data = csi300.history(period="max", interval="1mo")
    
    # 检查是否有分红数据
    if 'Dividends' not in data.columns:
        data['Dividends'] = 0.0
    
    # 创建年度数据存储
    yearly_returns = {}
    price_returns = {}
    dividend_returns = {}
    missing_dividend_years = []
    
    # Step 2: 计算每年的收益
    data['Year'] = data.index.year
    for year in data['Year'].unique():
        yearly_data = data[data['Year'] == year]
        if yearly_data.empty:
            continue
        # 计算年初和年末的价格
        start_price = yearly_data['Close'].iloc[0]
        end_price = yearly_data['Close'].iloc[-1]
        # 计算分红收益
        dividends = yearly_data['Dividends'].sum()
        if dividends == 0:
            missing_dividend_years.append(year)
        # 计算价格变动收益
        price_return = (end_price - start_price) / start_price * 100
        # 计算分红收益率
        dividend_return = (dividends) / start_price * 100
        # 存储数据
        price_returns[year] = price_return
        dividend_returns[year] = dividend_return
        yearly_returns[year] = price_return + dividend_return
    
    # 如果有年份缺少分红数据，给出警告
    if missing_dividend_years:
        missing_years_str = ', '.join(map(str, sorted(missing_dividend_years)))
        print(f"请注意，以下年份由于没有分红数据，请谨慎使用该数据：{missing_years_str}")
    
    # 确保年份按顺序排列
    years = sorted(yearly_returns.keys())
    price_vals = [price_returns[year] for year in years]
    dividend_vals = [dividend_returns[year] for year in years]
    
    # Step 3: 画出堆叠柱状图
    plt.figure(figsize=(14, 8))
    
    # 画价格变动收益的柱子
    bars1 = plt.bar(years, price_vals, color='skyblue', label='价格变动收益')
    
    # 画分红收益的柱子，叠加在价格变动收益上
    bars2 = plt.bar(years, dividend_vals, bottom=price_vals, color='lightgreen', label='分红收益')
    
    # 在柱子上显示数值
    for i in range(len(years)):
        plt.text(years[i], price_vals[i] + dividend_vals[i] + 0.1, f'{yearly_returns[years[i]]:.2f}%', 
                 ha='center', va='bottom', fontsize=8)
    
    plt.xlabel('年份')
    plt.ylabel('总回报率 (%)')
    plt.title('CSI 300年总回报率（价格变动 + 分红）')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    calculate_and_plot_csi300_return() 