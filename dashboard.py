import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from dash.dependencies import Output, Input

app = dash.Dash(__name__)
app.title = "Pi Network Dashboard"

def get_data():
    df = pd.read_csv("pi_network_prices.csv", names=["Timestamp", "Price"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df

app.layout = html.Div([
    html.H1("PI Price Dashboard"),
    dcc.Graph(id='price-chart'),
    html.Div(id="latest-price"),
    dcc.Interval(
        id='interval-component',
        interval=5 * 60 * 1000,  # 5 minutes in milliseconds
        n_intervals=0
    )
])

@app.callback(
    Output('price-chart', 'figure'),
    Output('latest-price', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_dashboard(_):
    df = get_data()
    fig = px.line(df, x="Timestamp", y="Price", title="Pi Price Over Time")
    latest_price = f"Latest Price: ${df.iloc[-1]['Price']}"
    return fig, latest_price

app.run(debug=True, host="0.0.0.0", port=8050)