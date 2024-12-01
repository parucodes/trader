import yfinance as yf
import pandas as pd
import config

def download_stock_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(interval=config.TIME_INTERVAL, start=config.START_DATE, end=config.END_DATE)
    data['Symbol'] = symbol  # Add symbol column to the data
    return data
