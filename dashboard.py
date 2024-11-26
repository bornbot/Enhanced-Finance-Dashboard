import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from data_retrieval import get_weekly_data
from risk_metrics import calculate_portfolio_metrics

# Initialize Dash App
dash_app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    url_base_pathname='/dashboard/'
)

# Define Layout
dash_app.layout = html.Div([
    html.Div([
        html.H1("Enhanced Financial Dashboard", style={'textAlign': 'center', 'fontSize': '2.5em'}),
    ]),
    # KPIs
    html.Div([
        html.Div([html.H4("Portfolio Return"), html.P(id="portfolio-return")], className="metric-box"),
        html.Div([html.H4("Portfolio Volatility"), html.P(id="portfolio-volatility")], className="metric-box"),
        html.Div([html.H4("Sharpe Ratio"), html.P(id="sharpe-ratio")], className="metric-box"),
        html.Div([html.H4("Maximum Drawdown"), html.P(id="max-drawdown")], className="metric-box"),
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),

    # Cumulative Returns and Risk-Return Scatterplot
    html.Div([
        html.Div([
            dcc.Graph(id="cumulative-returns-chart", style={'width': '100%'}),
            html.P("This graph shows the cumulative returns for the portfolio over time.", style={'textAlign': 'center'})
        ], style={
            'width': '48%',
            'display': 'inline-block',
            'padding': '10px',
            'boxShadow': '5px 5px 15px rgba(0,0,0,0.3)',
            'border': '2px solid #007bff',
            'borderRadius': '10px',
            'backgroundColor': 'white'
        }),
        html.Div([
            dcc.Graph(id="risk-return-scatter", style={'width': '100%'}),
            html.P("This scatterplot visualizes the relationship between portfolio risk (volatility) and return.", style={'textAlign': 'center'})
        ], style={
            'width': '48%',
            'display': 'inline-block',
            'padding': '10px',
            'boxShadow': '5px 5px 15px rgba(0,0,0,0.3)',
            'border': '2px solid #007bff',
            'borderRadius': '10px',
            'backgroundColor': 'white'
        }),
    ]),

    # Allocation Pie Chart and Returns Histogram
    html.Div([
        html.Div([
            dcc.Graph(id="allocation-pie", style={'width': '100%'}),
            html.P("This chart illustrates the weight distribution of the assets in the portfolio.", style={'textAlign': 'center'})
        ], style={
            'width': '48%',
            'display': 'inline-block',
            'padding': '10px',
            'boxShadow': '5px 5px 15px rgba(0,0,0,0.3)',
            'border': '2px solid #007bff',
            'borderRadius': '10px',
            'backgroundColor': 'white'
        }),
        html.Div([
            dcc.Graph(id="returns-histogram", style={'width': '100%'}),
            html.P("This histogram shows the frequency distribution of portfolio returns.", style={'textAlign': 'center'})
        ], style={
            'width': '48%',
            'display': 'inline-block',
            'padding': '10px',
            'boxShadow': '5px 5px 15px rgba(0,0,0,0.3)',
            'border': '2px solid #007bff',
            'borderRadius': '10px',
            'backgroundColor': 'white'
        }),
    ]),

    # Adjust Portfolio Weights
    html.Div([
        html.Label("Adjust Portfolio Weights:", style={'fontSize': '18px', 'textAlign': 'center'}),
        html.Div([
            dcc.Input(id="weight-aapl", type="number", placeholder="AAPL", value=0.3, style={'marginRight': '10px'}),
            dcc.Input(id="weight-msft", type="number", placeholder="MSFT", value=0.3, style={'marginRight': '10px'}),
            dcc.Input(id="weight-googl", type="number", placeholder="GOOGL", value=0.4, style={'marginRight': '10px'}),
        ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '20px'}),
    ]),
])


# Define Callbacks
@dash_app.callback(
    [Output("portfolio-return", "children"),
     Output("portfolio-volatility", "children"),
     Output("sharpe-ratio", "children"),
     Output("max-drawdown", "children"),
     Output("cumulative-returns-chart", "figure"),
     Output("risk-return-scatter", "figure"),
     Output("allocation-pie", "figure"),
     Output("returns-histogram", "figure")],
    [Input("weight-aapl", "value"),
     Input("weight-msft", "value"),
     Input("weight-googl", "value")]
)
def update_dashboard(weight_aapl, weight_msft, weight_googl):
    tickers = ["AAPL", "MSFT", "GOOGL"]
    weights = [weight_aapl, weight_msft, weight_googl]

    # Debug Weights
    print("Received Weights:", weights)
    if sum(weights) == 0:
        print("Weights sum to zero. Returning placeholders.")
        return "N/A", "N/A", "N/A", "N/A", go.Figure(), go.Figure(), go.Figure(), go.Figure()
    if sum(weights) != 1:
        weights = [w / sum(weights) for w in weights]
        print("Normalized Weights:", weights)

    # Fetch Data
    data = get_weekly_data(tickers)
    if data.empty:
        print("No data fetched. Using mock data.")
        data = pd.DataFrame(
            np.random.random((100, 3)) * 100,
            index=pd.date_range("2022-01-01", periods=100),
            columns=tickers
        )

    print("Fetched DataFrame:")
    print(data.head())

    # Calculate Metrics
    try:
        metrics = calculate_portfolio_metrics(data, weights)
        print("Calculated Metrics:")
        print(metrics)
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        metrics = {"Portfolio Return": 0, "Portfolio Volatility": 0, "Sharpe Ratio": 0, "Maximum Drawdown": 0}

    portfolio_return = f"{metrics.get('Portfolio Return', 0):.2%}"
    portfolio_volatility = f"{metrics.get('Portfolio Volatility', 0):.2%}"
    sharpe_ratio = f"{metrics.get('Sharpe Ratio', 0):.2f}"
    max_drawdown = f"{metrics.get('Maximum Drawdown', 0):.2%}"

    # Cumulative Returns Chart
    cumulative_returns = (1 + data.pct_change()).cumprod()
    cumulative_chart = go.Figure()
    for ticker in tickers:
        cumulative_chart.add_trace(go.Scatter(
            x=cumulative_returns.index,
            y=cumulative_returns[ticker],
            mode='lines',
            name=ticker,
            line=dict(width=2)
        ))
    cumulative_chart.update_layout(
        title="Cumulative Returns Over Time",
        xaxis_title="Date",
        yaxis_title="Cumulative Return",
        template="plotly_white"
    )

    # Risk-Return Scatterplot
    risk_return_scatter = go.Figure(data=[
        go.Scatter(
            x=[metrics['Portfolio Volatility']],
            y=[metrics['Portfolio Return']],
            mode='markers',
            marker=dict(size=15, color='blue', line=dict(width=2, color='darkblue')),
            name="Portfolio"
        )
    ])
    risk_return_scatter.update_layout(
        title="Risk vs. Return",
        xaxis_title="Volatility (Risk)",
        yaxis_title="Return",
        template="plotly_white"
    )

    # Allocation Pie Chart
    allocation_pie = go.Figure(data=[
        go.Pie(labels=tickers, values=weights, hole=0.4)
    ])
    allocation_pie.update_layout(
        title="Portfolio Allocation",
        annotations=[dict(text="Allocation", x=0.5, y=0.5, font_size=15, showarrow=False)],
        template="plotly_white"
    )

    # Returns Histogram
    returns_histogram = go.Figure(data=[
        go.Histogram(
            x=data.pct_change().stack(),
            nbinsx=30,
            marker_color='purple'
        )
    ])
    returns_histogram.update_layout(
        title="Distribution of Returns",
        xaxis_title="Return",
        yaxis_title="Frequency",
        template="plotly_white"
    )

    return portfolio_return, portfolio_volatility, sharpe_ratio, max_drawdown, cumulative_chart, risk_return_scatter, allocation_pie, returns_histogram
