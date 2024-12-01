import pandas as pd
import config

def backtest(data: pd.DataFrame, stock_symbol: str, strategy_name: str):
    balance = config.INITIAL_BALANCE
    position = 0
    entry_price = 0
    entry_time = None
    exit_time = None
    in_trade = False
    trade_type = None  # "buy" for long trades, "sell" for short trades
    take_profit = config.TAKE_PROFIT_PERCENT / 100
    stop_loss = config.STOP_LOSS_PERCENT / 100
    trailing_stop_loss = config.TRAILING_STOP_LOSS_PERCENT / 100
    trades = []
    
    # Initialize new columns in the DataFrame
    data['Profit/Loss'] = 0.0
    data['Balance'] = float(balance)
    data['In_Trade'] = 0
    data['Position'] = 0.0
    data['Entry_Price'] = 0.0
    data['Trade_Type'] = None
    
    # Variables for trailing stop loss
    highest_price_since_entry = 0
    lowest_price_since_entry = float('inf')
    
    # Reset index to ensure integer index
    data = data.reset_index()
    
    for i in range(len(data)):
        if data.iloc[i]['Signal'] == 'Buy' and not in_trade:
            position = balance / data.iloc[i]['Close']
            entry_price = data.iloc[i]['Close']
            entry_time = data.iloc[i]['Date']  # Assuming 'Date' column is present in the data
            balance -= position * entry_price
            in_trade = True
            trade_type = 'buy'
            highest_price_since_entry = entry_price  # Initialize highest price for trailing stop loss
        elif data.iloc[i]['Signal'] == 'Sell' and not in_trade:
            position = balance / data.iloc[i]['Close']
            entry_price = data.iloc[i]['Close']
            entry_time = data.iloc[i]['Date']  # Assuming 'Date' column is present in the data
            balance += position * entry_price  # Balance should reflect short sell
            in_trade = True
            trade_type = 'sell'
            lowest_price_since_entry = entry_price  # Initialize lowest price for trailing stop loss
        elif data.iloc[i]['Signal'] == 'Sell' and in_trade and trade_type == 'buy':
            balance += position * data.iloc[i]['Close']
            exit_price = data.iloc[i]['Close']
            exit_time = data.iloc[i]['Date']
            profit_loss = (exit_price - entry_price) * position
            trades.append([stock_symbol, strategy_name, trade_type.capitalize(), entry_time, exit_time, entry_price, exit_price, 'Signal', profit_loss])
            position = 0
            in_trade = False
            trade_type = None
        elif data.iloc[i]['Signal'] == 'Buy' and in_trade and trade_type == 'sell':
            balance -= position * data.iloc[i]['Close']
            exit_price = data.iloc[i]['Close']
            exit_time = data.iloc[i]['Date']
            profit_loss = (entry_price - exit_price) * position
            trades.append([stock_symbol, strategy_name, trade_type.capitalize(), entry_time, exit_time, entry_price, exit_price, 'Signal', profit_loss])
            position = 0
            in_trade = False
            trade_type = None
        
        # Check for take profit, stop loss, and trailing stop loss conditions
        if in_trade:
            if trade_type == 'buy':
                highest_price_since_entry = max(highest_price_since_entry, data.iloc[i]['Close'])
                trailing_stop_loss_price = highest_price_since_entry * (1 - trailing_stop_loss)
                if data.iloc[i]['Close'] >= entry_price * (1 + take_profit):
                    balance += position * data.iloc[i]['Close']
                    exit_price = data.iloc[i]['Close']
                    exit_time = data.iloc[i]['Date']
                    profit_loss = (exit_price - entry_price) * position
                    trades.append([stock_symbol, strategy_name, trade_type.capitalize(), entry_time, exit_time, entry_price, exit_price, 'Take Profit', profit_loss])
                    position = 0
                    in_trade = False
                    trade_type = None
                elif data.iloc[i]['Close'] <= entry_price * (1 - stop_loss) or data.iloc[i]['Close'] <= trailing_stop_loss_price:
                    balance += position * data.iloc[i]['Close']
                    exit_price = data.iloc[i]['Close']
                    exit_time = data.iloc[i]['Date']
                    reason = 'Stop Loss' if data.iloc[i]['Close'] <= entry_price * (1 - stop_loss) else 'Trailing Stop Loss'
                    profit_loss = (exit_price - entry_price) * position
                    trades.append([stock_symbol, strategy_name, trade_type.capitalize(), entry_time, exit_time, entry_price, exit_price, reason, profit_loss])
                    position = 0
                    in_trade = False
                    trade_type = None
            elif trade_type == 'sell':
                lowest_price_since_entry = min(lowest_price_since_entry, data.iloc[i]['Close'])
                trailing_stop_loss_price = lowest_price_since_entry * (1 + trailing_stop_loss)
                if data.iloc[i]['Close'] <= entry_price * (1 - take_profit):
                    balance -= position * data.iloc[i]['Close']
                    exit_price = data.iloc[i]['Close']
                    exit_time = data.iloc[i]['Date']
                    profit_loss = (entry_price - exit_price) * position
                    trades.append([stock_symbol, strategy_name, trade_type.capitalize(), entry_time, exit_time, entry_price, exit_price, 'Take Profit', profit_loss])
                    position = 0
                    in_trade = False
                    trade_type = None
                elif data.iloc[i]['Close'] >= entry_price * (1 + stop_loss) or data.iloc[i]['Close'] >= trailing_stop_loss_price:
                    balance -= position * data.iloc[i]['Close']
                    exit_price = data.iloc[i]['Close']
                    exit_time = data.iloc[i]['Date']
                    reason = 'Stop Loss' if data.iloc[i]['Close'] >= entry_price * (1 + stop_loss) else 'Trailing Stop Loss'
                    profit_loss = (entry_price - exit_price) * position
                    trades.append([stock_symbol, strategy_name, trade_type.capitalize(), entry_time, exit_time, entry_price, exit_price, reason, profit_loss])
                    position = 0
                    in_trade = False
                    trade_type = None
        
        # Maintain balance and profit/loss calculations
        if in_trade:
            if trade_type == 'buy':
                data.at[i, 'Profit/Loss'] = float((position * data.iloc[i]['Close']) - (position * entry_price))
                data.at[i, 'Balance'] = float(balance + (position * data.iloc[i]['Close']))
            elif trade_type == 'sell':
                data.at[i, 'Profit/Loss'] = float((position * entry_price) - (position * data.iloc[i]['Close']))
                data.at[i, 'Balance'] = float(balance - (position * data.iloc[i]['Close']))
        else:
            data.at[i, 'Profit/Loss'] = float(balance - config.INITIAL_BALANCE)
            data.at[i, 'Balance'] = float(balance)
        
        # Update DataFrame with current trade state
        data.at[i, 'In_Trade'] = int(in_trade)
        data.at[i, 'Position'] = position
        data.at[i, 'Entry_Price'] = entry_price
        data.at[i, 'Trade_Type'] = trade_type
    
    return data, trades
