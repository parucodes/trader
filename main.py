import importlib
import config
import data_downloader
import reporter
import backtester

def main():
    all_trades = []
    for symbol in config.STOCK_SYMBOLS:
        data = data_downloader.download_stock_data(symbol)
        
        for strategy_name in config.STRATEGIES:
            # Import the strategy module based on the config
            strategy_module = importlib.import_module(f'strategy.{strategy_name}')
            data_with_signals = strategy_module.generate_signals(data.copy())  # Use a copy to avoid modifying the original data
            
            # Apply backtesting
            data_with_results, trades = backtester.backtest(data_with_signals, symbol, strategy_name)
            all_trades.extend(trades)
            
            # Save individual stock data to CSV
            reporter.save_stock_data_to_csv(data_with_results, f"{symbol}_{strategy_name}_stock_data_with_signals_and_profit_loss.csv")
    
    # Generate trade report for all stocks and strategies
    reporter.generate_trade_report(all_trades, "trade_report.csv")
    
    # Generate trade summary for all stocks and strategies
    reporter.generate_trade_summary(all_trades, "trade_summary.csv")

if __name__ == "__main__":
    main()
