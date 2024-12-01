import os
import pandas as pd
import config

# Create reports directory if it doesn't exist
if not os.path.exists('reports'):
    os.makedirs('reports')

def save_stock_data_to_csv(data: pd.DataFrame, filename: str):
    filepath = os.path.join('reports', filename)
    data.to_csv(filepath, index=True)

def generate_trade_report(trades: list, filename: str):
    columns = ["Stock Symbol", "Strategy Name", "Trade Type", "Trade Entry Time", "Trade Exit Time", "Entry Price", "Exit Price", "Reason for Exit", "Profit/Loss"]
    report_df = pd.DataFrame(trades, columns=columns)
    filepath = os.path.join('reports', filename)
    report_df.to_csv(filepath, index=False)

def generate_trade_summary(trades: list, filename: str):
    columns = ["Stock Symbol", "Strategy Name", "Trade Type", "Number of Trades", "Number of Winning Trades", "Number of Losing Trades", "Total Profit/Loss", "Profit/Loss per Trade", "Median Profit/Loss"]
    summary_data = []

    for symbol in config.STOCK_SYMBOLS:
        for strategy_name in config.STRATEGIES:
            for trade_type in ["Buy", "Sell"]:
                symbol_strategy_trades = [trade for trade in trades if trade[0] == symbol and trade[1] == strategy_name and trade[2] == trade_type]
                num_trades = len(symbol_strategy_trades)
                num_winning_trades = len([trade for trade in symbol_strategy_trades if trade[-1] > 0])
                num_losing_trades = len([trade for trade in symbol_strategy_trades if trade[-1] <= 0])
                total_profit_loss = sum(trade[-1] for trade in symbol_strategy_trades)
                profit_loss_per_trade = total_profit_loss / num_trades if num_trades else 0
                median_profit_loss = pd.Series([trade[-1] for trade in symbol_strategy_trades]).median()

                summary_data.append([
                    symbol,
                    strategy_name,
                    trade_type,
                    num_trades,
                    num_winning_trades,
                    num_losing_trades,
                    total_profit_loss,
                    profit_loss_per_trade,
                    median_profit_loss
                ])
    
    summary_df = pd.DataFrame(summary_data, columns=columns)
    filepath = os.path.join('reports', filename)
    summary_df.to_csv(filepath, index=False)
