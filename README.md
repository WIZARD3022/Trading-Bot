# Trading Bot - Binance Futures Testnet

A lightweight Python application for placing orders on Binance Futures Testnet (USDT-M). Built with proper error handling, logging, and clean architecture.

## Features

✅ **Order Types:**
- Market Orders (BUY/SELL)
- Limit Orders (BUY/SELL)

✅ **Core Capabilities:**
- Place orders via CLI
- View account information
- List open orders
- Check server time

✅ **Quality:**
- Structured code with separate layers (client, orders, validators)
- Comprehensive logging to file and console
- Input validation and error handling
- Clean CLI with argparse

## Setup

### Prerequisites
- Python 3.8+
- pip
- Binance Futures Testnet Account with API credentials

### 1. Get Binance Testnet Credentials

1. Register at [Binance Testnet](https://testnet.binancefuture.com/)
2. Generate API Key and Secret from Account settings
3. Keep them safe!

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Set your API credentials as environment variables:

**On Windows (PowerShell):**
```powershell
$env:BNB_API_KEY = "your_api_key_here"
$env:BNB_API_SECRET = "your_api_secret_here"
```

**On Windows (CMD):**
```cmd
set BNB_API_KEY=your_api_key_here
set BNB_API_SECRET=your_api_secret_here
```

**On Linux/macOS:**
```bash
export BNB_API_KEY="your_api_key_here"
export BNB_API_SECRET="your_api_secret_here"
```

## Usage

### Place a Market Order

**BUY 0.001 BTC:**
```bash
python cli.py -s BTCUSDT -sd BUY -t MARKET -q 0.001
```

**SELL 1 ETH:**
```bash
python cli.py -s ETHUSDT -sd SELL -t MARKET -q 1.0
```

### Place a Limit Order

**BUY 0.001 BTC at $50,000:**
```bash
python cli.py -s BTCUSDT -sd BUY -t LIMIT -q 0.001 -p 50000.00
```

**SELL 1 ETH at $3,000:**
```bash
python cli.py -s ETHUSDT -sd SELL -t LIMIT -q 1.0 -p 3000.00
```

### Get Account Information

```bash
python cli.py --info
```

Output includes available balance and locked balance for each asset.

### List Open Orders

```bash
python cli.py --open-orders
```

### Check Server Time

```bash
python cli.py --server-time
```

## Project Structure

```
trading_bot/
├── __init__.py              # Package initialization
├── client.py                # Binance Futures API client wrapper
├── orders.py                # Order placement and management logic
├── validators.py            # Input validation
└── logging_config.py        # Logging setup

cli.py                        # CLI entry point
requirements.txt             # Python dependencies
README.md                     # This file
logs/                         # Log files (auto-created)
```

## Logging

The application creates detailed log files in the `logs/` directory. Each run generates a timestamped log file with:

- **API Requests/Responses:** All communication with Binance API
- **Order Events:** Order placement, success/failure
- **Errors:** Detailed error messages with stack traces
- **Debug Info:** Parameter validation, internal operations

Example log file: `logs/trading_bot_20240115_143022.log`

**Log Levels:**
- **DEBUG:** Detailed diagnostic info (API calls, parameters)
- **INFO:** General informational messages (order placed, account fetched)
- **ERROR:** Error conditions (API failures, validation errors)

## Example Log Output

```
2024-01-15 14:30:22 - trading_bot - INFO - Binance Futures Client initialized for testnet: https://testnet.binancefuture.com
2024-01-15 14:30:22 - trading_bot - DEBUG - API Request: POST /fapi/v1/order | Params: {'symbol': 'BTCUSDT', 'side': 'BUY', 'type': 'MARKET', 'quantity': 0.001, 'timestamp': 1705333822123}
2024-01-15 14:30:23 - trading_bot - DEBUG - API Response Status: 200
2024-01-15 14:30:23 - trading_bot - INFO - Order placed successfully: 123456789
2024-01-15 14:30:23 - trading_bot - INFO - MARKET order placed successfully: OrderID=123456789, Status=FILLED, ExecutedQty=0.001, AvgPrice=42500.50
```

## Error Handling

The application handles:

- **Invalid Input:** Symbol validation, quantity/price checks
- **API Errors:** Network failures, invalid API calls
- **Missing Credentials:** Clear error if env vars not set
- **Validation Errors:** Clear messages for invalid parameters

Example errors:
```
✗ Validation Error: Symbol 'BTC' appears invalid (too short)
✗ Validation Error: Price must be greater than 0, got -100
✗ API Error 400: {"code":-1111,"msg":"Precision is over the maximum defined for this asset."}
```

## API Reference

### BinanceFuturesClient

**Initialization:**
```python
from trading_bot.client import BinanceFuturesClient

client = BinanceFuturesClient(api_key, api_secret)
```

**Methods:**
- `place_order(symbol, side, type_, quantity, price=None)` - Place order
- `get_account_info()` - Get account details
- `get_open_orders(symbol=None)` - List open orders
- `cancel_order(symbol, order_id)` - Cancel order
- `get_order_status(symbol, order_id)` - Get order status
- `check_server_time()` - Check server time

### OrderManager

```python
from trading_bot.orders import OrderManager

manager = OrderManager(client)
response = manager.place_market_order("BTCUSDT", OrderSide.BUY, 0.001)
response = manager.place_limit_order("BTCUSDT", OrderSide.BUY, 0.001, 50000.00)
```

### Validators

```python
from trading_bot.validators import validate_order_params

symbol, side, order_type, quantity, price = validate_order_params(
    symbol="BTCUSDT",
    side="BUY",
    order_type="LIMIT",
    quantity="0.001",
    price="50000.00"
)
```

## Testing

To test without real orders, use the Testnet. **All orders are placed on testnet only.**

### Test Scenarios

1. **Market Buy Order:**
   ```bash
   python cli.py -s BTCUSDT -sd BUY -t MARKET -q 0.001
   ```

2. **Limit Sell Order:**
   ```bash
   python cli.py -s ETHUSDT -sd SELL -t LIMIT -q 1.0 -p 3000.00
   ```

3. **Check logs:**
   ```bash
   type logs/trading_bot_*.log  # Windows
   cat logs/trading_bot_*.log   # Linux/macOS
   ```

## Assumptions

1. **Testnet Only:** This application connects to Binance Futures Testnet (`testnet.binancefuture.com`). It will NOT work with mainnet.

2. **USDT Futures:** Orders are placed on USDT-M (Margin) contracts only.

3. **GTC Time in Force:** Limit orders use "Good Till Cancelled" (GTC) by default.

4. **Single-sided Orders:** Only market and limit orders are supported (no OCO, Stop-Limit, or Grid orders in base version).

5. **Quantity Precision:** Binance enforces quantity and price precision per symbol. Invalid precision will return API errors.

6. **API Rate Limits:** Binance has rate limits. The application respects these with proper error handling.

## Troubleshooting

### "API credentials not found"
- Ensure environment variables are set:
  ```bash
  echo %BNB_API_KEY%  # Windows
  echo $BNB_API_KEY   # Linux/macOS
  ```

### "Invalid API Key"
- Verify credentials are correct
- Ensure API key has "Futures" permissions enabled

### "Precision is over maximum"
- Use valid quantity/price for the symbol
- Check Binance documentation for symbol limits

### "Insufficient Balance"
- Add funds to testnet account
- Check balance with: `python cli.py --info`

### No orders placed (silently fails)
- Check logs in `logs/` directory
- Ensure API key has "Trade" permission

## Limitations

- Market orders execute at current market price (may slip)
- No advanced order types (OCO, Stop-Limit, Grid, etc.)
- No position management or risk controls
- CLI-only (no web UI in base version)

## License

This is a test assignment. Use for educational purposes only.

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Verify Binance API credentials
3. Ensure testnet account has balance
4. Check Binance Futures Testnet documentation

---

