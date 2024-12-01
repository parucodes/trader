import pandas as pd

def calculate_rsi(data: pd.DataFrame, period: int = 14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def generate_signals(data: pd.DataFrame):
    data['RSI'] = calculate_rsi(data)
    data['Signal'] = 'Hold'
    data.loc[data['RSI'] < 30, 'Signal'] = 'Buy'
    data.loc[data['RSI'] > 70, 'Signal'] = 'Sell'
    return data
