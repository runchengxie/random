import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex

def create_risk_return_diagram():
    # Parameters
    returns_asset1 = 0.1
    returns_asset2 = 0.15
    risk_asset1 = 0.2
    risk_asset2 = 0.25
    correlations = np.linspace(-1, 1, 201)  # Finer correlation steps
    weights = np.linspace(0, 1, 100)  # 100 different portfolio weights

    traces = []
    for corr in correlations:
        portfolio_returns = []
        portfolio_risks = []
        
        for w in weights:
            # Calculate portfolio metrics for different weights
            w1 = w
            w2 = 1 - w
            port_return = w1 * returns_asset1 + w2 * returns_asset2
            port_risk = np.sqrt(w1**2 * risk_asset1**2 + w2**2 * risk_asset2**2 + 
                              2 * w1 * w2 * corr * risk_asset1 * risk_asset2)
            
            portfolio_returns.append(port_return)
            portfolio_risks.append(port_risk)
        
        traces.append(go.Scatter(
            x=portfolio_risks,
            y=portfolio_returns,
            mode='lines',
            line=dict(color=to_hex(plt.cm.viridis((corr + 1) / 2))),
            name=f'Corr: {corr:.2f}',
            visible=(corr == 0)  # Only show correlation=0 initially
        ))

    # Create slider steps
    steps = []
    for i, corr in enumerate(correlations):
        step = dict(
            method='update',
            args=[{'visible': [False] * len(traces)},
                  {'title': f'Correlation: {corr:.2f}'}],
            label=f'{corr:.2f}'
        )
        step['args'][0]['visible'][i] = True
        steps.append(step)

    sliders = [dict(
        active=100,  # Start at correlation=0 (index 100)
        currentvalue={'prefix': 'Correlation: '},
        pad={'t': 50},
        steps=steps
    )]

    fig = go.Figure(data=traces)
    fig.update_layout(
        title='Portfolio Risk-Return Frontier',
        xaxis_title='Risk (Standard Deviation)',
        yaxis_title='Expected Return',
        xaxis=dict(range=[0, max(risk_asset1, risk_asset2) * 1.2]),
        yaxis=dict(range=[min(returns_asset1, returns_asset2) * 0.8, 
                         max(returns_asset1, returns_asset2) * 1.2]),
        sliders=sliders
    )
    fig.show()

if __name__ == "__main__":
    create_risk_return_diagram()
