{
    "trading_platform": {
        "max_trade_amount": 100,  // Maximum amount of energy that can be traded (kWh)
        "min_trade_amount": 1,    // Minimum amount of energy that can be traded (kWh)
        "trade_interval": "15m",  // Interval for new trades (e.g., "15m" for 15 minutes)
        "trade_fee_percentage": 0.02, // Fee on each trade as a percentage (2%)
        "currency": "USD",  // Currency for transactions
        "transaction_timeout": 600,  // Timeout for confirming a trade (seconds)
        "dynamic_pricing": true,  // Whether dynamic pricing should be enabled for trading
        "pricing_model": "auction",  // The model for determining prices ("auction" or "fixed")
        "auction": {
            "initial_price": 0.1, // Initial price for energy in USD/kWh
            "price_adjustment_rate": 0.01, // Price adjustment per trade in USD/kWh
            "max_price": 1.0, // Maximum possible price in USD/kWh
            "min_price": 0.05 // Minimum possible price in USD/kWh
        }
    },
    "smart_contracts": {
        "enabled": true,  // Whether smart contracts are enabled for energy transactions
        "contract_template": "energy_trade_template",  // Template for smart contracts
        "gas_fee": 0.001,  // Gas fee for transaction execution
        "blockchain_platform": "Ethereum",  // Blockchain platform for smart contracts
        "contract_timeout": 3600  // Timeout for contract execution (seconds)
    },
    "transaction_history": {
        "enable_logging": true,  // Whether transaction history should be logged
        "log_file": "transactions.log",  // File to store transaction history
        "max_log_size_mb": 50  // Maximum size of the log file before it is rotated (MB)
    }
}
