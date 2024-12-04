import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import plotly.graph_objs as go

# 初始化 Dash 应用
app = dash.Dash(__name__)

# 初始参数
initial_returns_asset1 = 0.10
initial_returns_asset2 = 0.15
initial_risk_asset1 = 0.20
initial_risk_asset2 = 0.25
initial_correlation = 0.00

# 应用布局
app.layout = html.Div([
    html.Div([
        html.H3("投资组合参数设置"),
        
        html.Label('资产1 预期收益率'),
        dcc.Slider(
            id='return-asset1',
            min=0.05,
            max=0.15,
            step=0.01,
            value=initial_returns_asset1,
            marks={i: f"{i:.2f}" for i in np.linspace(0.05, 0.15, 3)}
        ),
        html.Br(),
        
        html.Label('资产2 预期收益率'),
        dcc.Slider(
            id='return-asset2',
            min=0.10,
            max=0.20,
            step=0.01,
            value=initial_returns_asset2,
            marks={i: f"{i:.2f}" for i in np.linspace(0.10, 0.20, 3)}
        ),
        html.Br(),
        
        html.Label('资产1 风险（标准差）'),
        dcc.Slider(
            id='risk-asset1',
            min=0.15,
            max=0.25,
            step=0.01,
            value=initial_risk_asset1,
            marks={i: f"{i:.2f}" for i in np.linspace(0.15, 0.25, 3)}
        ),
        html.Br(),
        
        html.Label('资产2 风险（标准差）'),
        dcc.Slider(
            id='risk-asset2',
            min=0.20,
            max=0.30,
            step=0.01,
            value=initial_risk_asset2,
            marks={i: f"{i:.2f}" for i in np.linspace(0.20, 0.30, 3)}
        ),
        html.Br(),
        
        html.Label('资产相关性'),
        dcc.Slider(
            id='correlation',
            min=-1.0,
            max=1.0,
            step=0.01,
            value=initial_correlation,
            marks={-1.0: '-1.00', 0.0: '0.00', 1.0: '1.00'}
        ),
    ], style={'width': '30%', 'display': 'inline-block', 'padding': '20px'}),
    
    html.Div([
        dcc.Graph(id='risk-return-graph')
    ], style={'width': '65%', 'display': 'inline-block', 'padding': '20px'}),
])

# 回调函数更新图表
@app.callback(
    Output('risk-return-graph', 'figure'),
    [
        Input('return-asset1', 'value'),
        Input('return-asset2', 'value'),
        Input('risk-asset1', 'value'),
        Input('risk-asset2', 'value'),
        Input('correlation', 'value')
    ]
)
def update_graph(ret1, ret2, risk1, risk2, corr):
    weights = np.linspace(0, 1, 100)
    portfolio_returns = ret1 * weights + ret2 * (1 - weights)
    
    # 计算投资组合方差和风险
    variance = (risk1**2 * weights**2 +
                risk2**2 * (1 - weights)**2 +
                2 * corr * risk1 * risk2 * weights * (1 - weights))
    portfolio_risks = np.sqrt(np.maximum(variance, 0))  # 确保方差非负
    
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
    
    # 添加左上角的注释框
    annotation_text = (
        f"相关性: {corr:.2f}<br>"
        f"资产1 权重: {optimal_weight:.2f}<br>"
        f"资产2 权重: {1 - optimal_weight:.2f}<br>"
        f"预期收益率: {optimal_return:.2f}<br>"
        f"风险 (标准差): {optimal_risk:.2f}"
    )
    
    fig.update_layout(
        annotations=[
            dict(
                text=annotation_text,
                x=0.05,
                y=0.95,
                xref='paper',
                yref='paper',
                showarrow=False,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='black',
                borderwidth=1
            )
        ],
        title='投资组合风险-收益前沿',
        xaxis_title='风险（标准差）',
        yaxis_title='预期收益率',
        xaxis=dict(range=[0, max(risk1, risk2)*1.2]),
        yaxis=dict(range=[min(ret1, ret2)*0.8, max(ret1, ret2)*1.2]),
        hovermode='closest'
    )
    
    return fig

# 运行应用
if __name__ == "__main__":
    app.run_server(debug=True, port=8051)