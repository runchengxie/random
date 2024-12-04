import streamlit as st
import numpy as np
import plotly.graph_objs as go

# 页面配置
st.set_page_config(page_title="投资组合优化", layout="wide")
st.title("投资组合优化分析")

# 侧边栏参数设置
st.sidebar.header("投资组合参数设置")

# 资产1参数
st.sidebar.subheader("资产1参数")
ret1 = st.sidebar.slider(
    "预期收益率 (资产1)",
    min_value=0.05,
    max_value=0.15,
    value=0.10,
    step=0.01,
    format="%.2f"
)

risk1 = st.sidebar.slider(
    "风险/标准差 (资产1)",
    min_value=0.15,
    max_value=0.25,
    value=0.20,
    step=0.01,
    format="%.2f"
)

# 资产2参数
st.sidebar.subheader("资产2参数")
ret2 = st.sidebar.slider(
    "预期收益率 (资产2)",
    min_value=0.10,
    max_value=0.20,
    value=0.15,
    step=0.01,
    format="%.2f"
)

risk2 = st.sidebar.slider(
    "风险/标准差 (资产2)",
    min_value=0.15,
    max_value=0.25,
    value=0.25,
    step=0.01,
    format="%.2f"
)

# 相关系数
corr = st.sidebar.slider(
    "资产相关系数",
    min_value=-1.0,
    max_value=1.0,
    value=0.0,
    step=0.1,
    format="%.1f"
)

# 计算投资组合数据
weights = np.linspace(0, 1, 100)
portfolio_returns = ret1 * weights + ret2 * (1 - weights)

# 计算投资组合方差和风险
variance = (risk1**2 * weights**2 +
           risk2**2 * (1 - weights)**2 +
           2 * corr * risk1 * risk2 * weights * (1 - weights))
portfolio_risks = np.sqrt(np.maximum(variance, 0))

# 找到最小风险点
min_risk_idx = np.argmin(portfolio_risks)
optimal_risk = portfolio_risks[min_risk_idx]
optimal_return = portfolio_returns[min_risk_idx]
optimal_weight = weights[min_risk_idx]

# 创建图表
fig = go.Figure()

# 添加效率前沿曲线
fig.add_trace(go.Scatter(
    x=portfolio_risks,
    y=portfolio_returns,
    mode='lines',
    name='效率前沿',
    line=dict(color='blue')
))

# 添加最优点标记
fig.add_trace(go.Scatter(
    x=[optimal_risk],
    y=[optimal_return],
    mode='markers',
    marker=dict(symbol='x', size=12, color='red'),
    name='最优点'
))

# 更新布局
fig.update_layout(
    title='投资组合风险-收益前沿',
    xaxis_title='风险（标准差）',
    yaxis_title='预期收益率',
    xaxis=dict(range=[0, max(risk1, risk2)*1.2]),
    yaxis=dict(range=[min(ret1, ret2)*0.8, max(ret1, ret2)*1.2]),
    hovermode='closest'
)

# 显示图表
st.plotly_chart(fig, use_container_width=True)

# 显示最优配置
col1, col2 = st.columns(2)
with col1:
    st.subheader("最优配置")
    st.write(f"资产1 权重: {optimal_weight:.2f}")
    st.write(f"资产2 权重: {1-optimal_weight:.2f}")
with col2:
    st.subheader("预期表现")
    st.write(f"预期收益率: {optimal_return:.2f}")
    st.write(f"风险 (标准差): {optimal_risk:.2f}")
