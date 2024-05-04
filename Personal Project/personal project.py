personal project

# %% Mutual Fund and ETF Analysis Tool
# Import necessary libraries for the web app
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import yfinance as yf

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout for the Dash app
app.layout = html.Div([
    html.H1('Mutual Fund and ETF Analysis Tool'),
    html.Div([
        html.P("Input Stock Tickers (separated by commas): "),
        dcc.Input(id='input-tickers', value='AAPL, MSFT, GOOGL', type='text'),
        html.Button(id='submit-button', n_clicks=0, children='Submit'),
        html.Div(id='output-container-button', children='Enter tickers and press submit')
    ]),
    dcc.Graph(id='portfolio-pie-chart'),
    dcc.Graph(id='candlestick-chart', style={'display': 'none'}),  # Initially hidden
    dcc.Graph(id='cumulative-returns-chart'),
    dcc.Graph(id='daily-returns-distribution-chart')
])

@app.callback(
    [Output('portfolio-pie-chart', 'figure'),
     Output('cumulative-returns-chart', 'figure'),
     Output('daily-returns-distribution-chart', 'figure'),
     Output('output-container-button', 'children')],
    [Input('submit-button', 'n_clicks')],
    [State('input-tickers', 'value')]
)
def update_output(n_clicks, tickers):
    if n_clicks > 0:
        try:
            ticker_list = [ticker.strip().upper() for ticker in tickers.split(',')]
            ticker_list.append('SPY')  # Always include SPY for market comparison
            start_date = '2021-01-01'
            end_date = '2024-04-30'
            portfolio_data = yf.download(ticker_list, start=start_date, end=end_date)['Adj Close']
        except Exception as e:
            return [go.Figure(), go.Figure(), go.Figure(), f"Error downloading data: {e}"]

        if portfolio_data.isnull().any().any():
            missing_data_tickers = portfolio_data.columns[portfolio_data.isnull().any()].tolist()
            return [go.Figure(), go.Figure(), go.Figure(), f"Missing data for {', '.join(missing_data_tickers)}. Please check ticker symbols and date range."]

        try:
            daily_returns = portfolio_data.pct_change()
            volatility = daily_returns.std()
            inverse_volatility = 1 / volatility
            weights = inverse_volatility[:-1] / inverse_volatility[:-1].sum()

            pie_chart = go.Figure(data=[go.Pie(labels=portfolio_data.columns[:-1], values=weights, textinfo='label+percent', hole=.3)])
            pie_chart.update_layout(title_text='Portfolio Allocation by Inverse Volatility', clickmode='event+select')

            portfolio_returns = daily_returns[portfolio_data.columns[:-1]].dot(weights)
            cumulative_portfolio_returns = (1 + portfolio_returns).cumprod() - 1
            spy_returns = daily_returns['SPY']
            cumulative_spy_returns = (1 + spy_returns).cumprod() - 1

            time_series_plot = go.Figure()
            time_series_plot.add_trace(go.Scatter(x=cumulative_portfolio_returns.index, y=cumulative_portfolio_returns * 100, mode='lines', name='Portfolio Returns'))
            time_series_plot.add_trace(go.Scatter(x=cumulative_spy_returns.index, y=cumulative_spy_returns * 100, mode='lines', name='Market Average (SPY)', line=dict(color='red')))
            time_series_plot.update_layout(title='Cumulative Portfolio Returns vs Market Average', xaxis_title='Date', yaxis_title='Cumulative Returns (%)')

            box_plot = go.Figure()
            for ticker in portfolio_data.columns[:-1]:  # Exclude SPY for the box plot
                box_plot.add_trace(go.Box(y=daily_returns[ticker], name=ticker))
            box_plot.update_layout(title='Distribution of Daily Returns for Each Company')

            return pie_chart, time_series_plot, box_plot, "Updated successfully with new tickers."
        except Exception as e:
            return [go.Figure(), go.Figure(), go.Figure(), f"Error processing data: {e}"]

    return [go.Figure(), go.Figure(), go.Figure(), "Enter tickers and press submit"]

# Run the server
import socket

web = "http://127.0.0.1:"
def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # Binding to port 0 lets the OS choose a free port
        return s.getsockname()[1]  # Return the port number assigned

if __name__ == '__main__':
    port = find_free_port()  # Find a free port
    app.run_server(debug=True, port=port)  # Run the server on the new port
    print(web + str(port))  # Print the web address to access the server

# %%
# Run the server
import socket

web = "http://127.0.0.1:"
def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # Binding to port 0 lets the OS choose a free port
        return s.getsockname()[1]  # Return the port number assigned

if __name__ == '__main__':
    port = find_free_port()  # Find a free port
    app.run_server(debug=True, port=port)  # Run the server on the new port
    print(web + str(port))  # Print the web address to access the server
