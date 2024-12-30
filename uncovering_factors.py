# 导入库
import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

# 删除或注释掉此行，因为它在脚本中无效
# %matplotlib inline

# 设置Tushare的Token
api_key = os.getenv('TUSHARE_API_KEY')
if not api_key:
    raise ValueError("请设置环境变量 TUSHARE_API_KEY 或在代码中直接输入 API Key。")
ts.set_token(api_key)
pro = ts.pro_api()

# 获取所有上市股票列表
stock_basic = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,market,list_date')

# 指定财务报表日期
report_date = '20221231'

# 获取市盈率（PE-TTM）
pe_data = pro.daily_basic(ts_code='', trade_date='20221230', fields='ts_code,pe_ttm')

# 合并数据
stock_data = pd.merge(stock_basic, pe_data, on='ts_code', how='left')

# 删除缺失值
stock_data = stock_data.dropna(subset=['pe_ttm'])

# 指定计算收益的起始和结束日期
start_date = '20230101'
end_date = '20230131'

# 获取前200只股票（示例）
sample_stocks = stock_data.head(200).copy()

# 批量获取指定日期范围内的所有股票行情数据
df_all = pro.daily(start_date=start_date, end_date=end_date)

# 将行情数据与样本股票列表进行合并
df_all = df_all[df_all['ts_code'].isin(sample_stocks['ts_code'])]

# 计算每只股票的月度收益率
returns = []
for code in sample_stocks['ts_code']:
    df = df_all[df_all['ts_code'] == code].sort_values(by='trade_date')
    if len(df) >= 2:
        start_price = df.iloc[0]['close']
        end_price = df.iloc[-1]['close']
        ret = (end_price - start_price) / start_price
    else:
        ret = np.nan
    returns.append(ret)

sample_stocks['monthly_return'] = returns

# 删除缺失收益率的股票
sample_stocks = sample_stocks.dropna(subset=['monthly_return'])

# 根据市盈率从低到高排序
sample_stocks = sample_stocks.sort_values(by='pe_ttm')

# 分为五组
sample_stocks['group'] = pd.qcut(sample_stocks['pe_ttm'], 5, labels=False)

# 计算每组的平均收益率
grouped = sample_stocks.groupby('group')
group_returns = grouped['monthly_return'].mean()

# 将分组编号转换为友好的名称
group_names = {
    0: '最低PE组',
    1: '较低PE组',
    2: '中等PE组',
    3: '较高PE组',
    4: '最高PE组'
}
group_returns.index = group_returns.index.map(group_names)

print("各组平均收益率：")
print(group_returns)

# 绘制柱状图
plt.figure(figsize=(10,6))
group_returns.plot(kind='bar')
plt.ylabel('平均收益率')
plt.title('不同PE分组的平均收益率对比')
plt.show()

# 统计检验
low_pe_returns = sample_stocks[sample_stocks['group'] == 0]['monthly_return']
high_pe_returns = sample_stocks[sample_stocks['group'] == 4]['monthly_return']

t_stat, p_value = stats.ttest_ind(low_pe_returns, high_pe_returns, equal_var=False)

print("最低PE组平均收益率：", low_pe_returns.mean())
print("最高PE组平均收益率：", high_pe_returns.mean())
print("t统计量：", t_stat)
print("p值：", p_value)