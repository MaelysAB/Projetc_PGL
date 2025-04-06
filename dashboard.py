import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from dash.dependencies import Output, Input
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import numpy as np

app = dash.Dash(__name__)
app.title = "Pi dashboard"

#We are loading the price of pi
def get_data():
    df = pd.read_csv("pi_network_prices.csv", names=["timestamp", "price", "date"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = pd.to_datetime(df["date"])
    return df

#We are creating a daily report
def get_daily_report(df):
    df['date'] = df['timestamp'].dt.date
    daily_data = df.groupby('date').agg(
        open_price=('price', 'first'),
        close_price=('price', 'last'),
        volatility=('price', lambda x: np.std(x)),
        evolution=('price', lambda x: (x.iloc[-1] - x.iloc[0]) / x.iloc[0] * 100)
    ).reset_index()
    today = pd.to_datetime("today").date()
    today_report = daily_data[daily_data['date'] == today]
    return today_report.iloc[0]


#We make sure the daily report is updated at 8 
def update_report_at_8():
    if datetime.datetime.now().hour == 20:
        df = get_data()
        today_report = get_daily_report(df)
        today_report.to_csv("daily_report.csv", index=False)
        print("The daily report is uploaded")

# We need a scheduler to schedule the uptdate
scheduler = BackgroundScheduler()
scheduler.add_job(update_report_at_8, 'interval', hours=1)
scheduler.start()

#this helps updatre the dashboard every 5 min
app.layout = html.Div([
    html.H1("Pi dashboard"),
    dcc.Graph(id='price-chart'),
    html.Div(id="latest-price"),
    html.Div(id="daily-report"),
    dcc.Interval(
        id='interval-component',
        interval=5 * 60 * 1000,  # 5 minutes
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
    fig = px.line(df, x="timestamp", y="price", title="Pi price over time")
    latest_price = f"Latest price: ${df.iloc[-1]['price']:.2f}"
    try:
        daily_report = pd.read_csv("daily_report.csv")
        daily_report_str = (
            f"today report (Date: {daily_report.iloc[0]['date']}):\n"
            f"open price: ${daily_report.iloc[0]['open_price']:.2f}\n"
            f"close price: ${daily_report.iloc[0]['close_price']:.2f}\n"
            f"daily volatility: ${daily_report.iloc[0]['volatility']:.2f}\n"
            f"price evolution: {daily_report.iloc[0]['evolution']:.2f}%"
        )
    except Exception:
        daily_report_str = "It is not 8pm yet so we cannot update the report yet"
    return fig, latest_price, daily_report_str

app.run(debug=True, host='0.0.0.0', port=8050)
