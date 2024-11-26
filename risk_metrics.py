import numpy as np

def calculate_portfolio_metrics(df, weights):
    """
    Calculate portfolio metrics: expected return, volatility, Sharpe ratio, VaR, and correlation matrix.
    """
    weights = np.array(weights)
    daily_returns = df.pct_change().dropna()

    if daily_returns.empty:
        raise ValueError("The daily returns DataFrame is empty. Ensure historical data is correctly populated.")

    portfolio_return = np.dot(daily_returns.mean(), weights) * 252
    portfolio_volatility = np.sqrt(np.dot(weights, np.dot(daily_returns.cov() * 252, weights)))
    sharpe_ratio = portfolio_return / portfolio_volatility
    VaR_95 = np.percentile(daily_returns.dot(weights), 5)
    correlation_matrix = daily_returns.corr()

    metrics = {
        'Portfolio Return': portfolio_return,
        'Portfolio Volatility': portfolio_volatility,
        'Sharpe Ratio': sharpe_ratio,
        'VaR (5%)': VaR_95,
        'Correlation Matrix': correlation_matrix
    }
    daily_returns = df.pct_change().dropna()
    print("Daily Returns:")
    print(daily_returns.head())

    print("Weights:")
    print(weights)

    cov_matrix = daily_returns.cov()
    print("Covariance Matrix:")
    print(cov_matrix)
    
    return metrics
