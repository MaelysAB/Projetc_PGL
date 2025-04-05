import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from dash.dependencies import Output, Input
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import numpy as np

app = dash.Dash(__name__)
app.title = "Pi Network Dashboard"

# Load data from CSV
def get_data():
    df = pd.read_csv("pi_network_prices.csv", names=["Timestamp", "Price", "Date"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df["Date"] = pd.to_datetime(df["Date"])
    return df

def get_daily_report(df):
    # Group data by date
    df['Date'] = df['Timestamp'].dt.date
    daily_data = df.groupby('Date').agg(
        open_price=('Price', 'first'),  # First entry in the day for open price
        close_price=('Price', 'last'),  # Last entry in the day for close price
        volatility=('Price', lambda x: np.std(x)),  # Standard deviation for daily volatility
        evolution=('Price', lambda x: (x.iloc[-1] - x.iloc[0]) / x.iloc[0] * 100)  # Evolution in percentage
    ).reset_index()

    # Get today's report (or most recent)
    today = pd.to_datetime("today").date()
    today_report = daily_data[daily_data['Date'] == today]

    if not today_report.empty:
        return today_report.iloc[0]
    return None


# Define function to update the report at 8 PM
def update_report_at_8pm():
    if datetime.datetime.now().hour == 20:  # 8 PM
        print("Updating daily report")
        # Call the function to update the report here
        df = get_data()
        today_report = get_daily_report(df)
        if today_report is not None:
            print(f"Today's Report (Date: {today_report['Date']}):\n"
                  f"Open Price: ${today_report['open_price']:.2f}\n"
                  f"Close Price: ${today_report['close_price']:.2f}\n"
                  f"Daily Volatility: ${today_report['volatility']:.2f}\n"
                  f"Price Evolution: {today_report['evolution']:.2f}%")
        else:
            print("No data available for today.")

# Setup the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(update_report_at_8pm, 'interval', hours=1)
scheduler.start()

app.layout = html.Div([
    html.H1("Pi Network Dashboard"),
    dcc.Graph(id='price-chart'),
    html.Div(id="latest-price"),
    html.Div(id="daily-report"),
    dcc.Interval(
        id='interval-component',
        interval=5 * 60 * 1000,  # 5 minutes in milliseconds
        n_intervals=0
    )
])

@app.callback(
    Output('price-chart', 'figure'),
    Output('latest-price', 'children'),
    Output('daily-report', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_dashboard(_):
    df = get_data()
    
    # Get the latest price data
    fig = px.line(df, x="Timestamp", y="Price", title="Pi Price Over Time")
    latest_price = f"Latest Price: ${df.iloc[-1]['Price']}"
    
    # Get the daily report
    daily_report = get_daily_report(df)
    if daily_report is not None:
        daily_report_str = (
            f"Today's Report (Date: {daily_report['Date']}):\n"
            f"Open Price: ${daily_report['open_price']:.2f}\n"
            f"Close Price: ${daily_report['close_price']:.2f}\n"
            f"Daily Volatility: ${daily_report['volatility']:.2f}\n"
            f"Price Evolution: {daily_report['evolution']:.2f}%"
        )
    else:
        daily_report_str = "No data available for today."

    return fig, latest_price, daily_report_str
app.run(debug=True)
