import pandas as pd

def calculate_moving_averages(data: pd.DataFrame, fast_period: int = 10, slow_period: int = 50):
    data['Fast_MA'] = data['Close'].rolling(window=fast_period).mean()
    data['Slow_MA'] = data['Close'].rolling(window=slow_period).mean()
    return data

def generate_signals(data: pd.DataFrame):
    data = calculate_moving_averages(data)
    data['Signal'] = 'Hold'
    data.loc[data['Fast_MA'] > data['Slow_MA'], 'Signal'] = 'Buy'
    data.loc[data['Fast_MA'] < data['Slow_MA'], 'Signal'] = 'Sell'
    return data
