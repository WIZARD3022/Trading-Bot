# Trading Bot - Usage Examples & Testing Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

**PowerShell (Windows):**
```powershell
$env:BNB_API_KEY = "your_binance_api_key"
$env:BNB_API_SECRET = "your_binance_api_secret"
```

**CMD (Windows):**
```cmd
set BNB_API_KEY=your_binance_api_key
set BNB_API_SECRET=your_binance_api_secret
```

**Bash (Linux/macOS):**
```bash
export BNB_API_KEY="your_binance_api_key"
export BNB_API_SECRET="your_binance_api_secret"
```

### 3. Run Examples

## Example 1: Place a Market Buy Order

```bash
python cli.py -s BTCUSDT -sd BUY -t MARKET -q 0.001
```

**Expected Output:**
```
============================================================
ORDER REQUEST SUMMARY
============================================================
Symbol:      BTCUSDT
Side:        BUY
Type:        MARKET
Quantity:    0.001
============================================================

============================================================
ORDER RESPONSE SUMMARY
============================================================
Order ID:        123456789
Symbol:          BTCUSDT
Side:            BUY
Type:            MARKET
Status:          FILLED
Quantity:        0.001
Executed Qty:    0.001
Price:           0
Avg Price:       42567.50
Commission:      0.00001
Commission Asset:USDT
Time:            1705333822456
============================================================
Order placed successfully!
```

**Log Entry:**
```
2024-01-15 14:30:22 - trading_bot - INFO - Placing MARKET BUY order: 0.001 BTCUSDT
2024-01-15 14:30:22 - trading_bot - DEBUG - API Request: POST /fapi/v1/order | Params: {...}
2024-01-15 14:30:22 - trading_bot - DEBUG - API Response Status: 200
2024-01-15 14:30:22 - trading_bot - INFO - Order placed successfully: 123456789
```

## Example 2: Place a Limit Sell Order

```bash
python cli.py -s ETHUSDT -sd SELL -t LIMIT -q 1.0 -p 3000.00
```

**Expected Output:**
```
============================================================
ORDER REQUEST SUMMARY
============================================================
Symbol:      ETHUSDT
Side:        SELL
Type:        LIMIT
Quantity:    1.0
Price:       3000.0
============================================================

============================================================
ORDER RESPONSE SUMMARY
============================================================
Order ID:        987654321
Symbol:          ETHUSDT
Side:            SELL
Type:            LIMIT
Status:          NEW
Quantity:        1.0
Executed Qty:    0.0
Price:           3000.0
Avg Price:       0.00
Commission:      0
Commission Asset:USDT
Time:            1705334110523
============================================================
Order placed successfully!
```

**Status: NEW** = Order is waiting for the market price to reach the limit price.

**Log Entry:**
```
2024-01-15 14:35:10 - trading_bot - INFO - Placing LIMIT SELL order: 1.0 ETHUSDT @ 3000.00
2024-01-15 14:35:10 - trading_bot - DEBUG - API Request: POST /fapi/v1/order | Params: {...}
2024-01-15 14:35:10 - trading_bot - DEBUG - API Response Status: 200
2024-01-15 14:35:10 - trading_bot - INFO - LIMIT order placed successfully: OrderID=987654321
```

## Example 3: Get Account Information

```bash
python cli.py --info
```

**Expected Output:**
```
============================================================
ACCOUNT INFORMATION
============================================================
Total Assets: 15

Balances (non-zero):
  USDT: Available=10000.0000, Locked=0.0
  BUSD: Available=5000.0000, Locked=0.0
  BTC: Available=0.5, Locked=0.1
============================================================
```

## Example 4: List Open Orders

```bash
python cli.py --open-orders
```

**Expected Output:**
```
============================================================
OPEN ORDERS
============================================================
Total Open Orders: 2

Order ID: 123456789
  Symbol: BTCUSDT
  Side: SELL
  Type: LIMIT
  Quantity: 0.001
  Price: 50000.00
  Status: NEW

Order ID: 987654321
  Symbol: ETHUSDT
  Side: BUY
  Type: LIMIT
  Quantity: 1.0
  Price: 2500.00
  Status: NEW

============================================================
```

## Example 5: Check Server Time

```bash
python cli.py --server-time
```

**Expected Output:**
```
Server Time: 1705334110523
```

## Testing Scenarios

### Scenario 1: Quick Market Order
**Objective:** Test basic market order placement

```bash
python cli.py -s BTCUSDT -sd BUY -t MARKET -q 0.001
```

**Success Criteria:**
- Order status is FILLED
- Executed Qty matches requested quantity
- Avg Price is populated
- Log file contains API request/response

### Scenario 2: Limit Order (Not Filled)
**Objective:** Test limit order creation

```bash
python cli.py -s ETHUSDT -sd SELL -t LIMIT -q 1.0 -p 10000.00
```

**Success Criteria:**
- Order status is NEW
- Executed Qty is 0 (not filled yet)
- Order remains in open orders
- Log file shows correct parameters

### Scenario 3: Input Validation
**Objective:** Test error handling for invalid inputs

**Invalid Symbol:**
```bash
python cli.py -s BTC -sd BUY -t MARKET -q 0.001
```
Expected: `Validation Error: Symbol 'BTC' appears invalid (too short)`

**Invalid Quantity:**
```bash
python cli.py -s BTCUSDT -sd BUY -t MARKET -q -0.001
```
Expected: `Validation Error: Quantity must be greater than 0, got -0.001`

**Missing Price for LIMIT:**
```bash
python cli.py -s BTCUSDT -sd BUY -t LIMIT -q 0.001
```
Expected: `Validation Error: Price is required for LIMIT orders`

### Scenario 4: API Error Handling
**Objective:** Test error handling for API failures

**With invalid credentials:**
```bash
python cli.py -s BTCUSDT -sd BUY -t MARKET -q 0.001
```
Expected: `API Error 401: Invalid API key`

## Log File Analysis

### Log File Locations
```
logs/trading_bot_20240115_143022.log    # Market order log
logs/trading_bot_20240115_143510.log    # Limit order log
```

### Key Log Entries to Look For

**1. Client Initialization:**
```
INFO - Binance Futures Client initialized for testnet: https://testnet.binancefuture.com
```

**2. API Request:**
```
DEBUG - API Request: POST /fapi/v1/order | Params: {...}
```

**3. API Response:**
```
DEBUG - API Response Status: 200
DEBUG - API Response: {'orderId': 123456789, ...}
```

**4. Order Placement:**
```
INFO - Placing MARKET BUY order: 0.001 BTCUSDT
INFO - Order placed successfully: 123456789
```

### Reading Logs

**View latest log:**
```bash
# Windows
type logs/trading_bot_*.log | tail -50

# Linux/macOS
tail -50 logs/trading_bot_*.log
```

**Search for errors:**
```bash
# Windows
findstr /I "ERROR" logs/trading_bot_*.log

# Linux/macOS
grep -i "ERROR" logs/trading_bot_*.log
```

## Code Quality Features

### 1. Structured Layers

**API Client Layer** (`trading_bot/client.py`):
- HMAC SHA256 signature generation
- Request/response handling
- Error management
- Timestamp synchronization

**Order Management Layer** (`trading_bot/orders.py`):
- Order placement logic
- Response formatting
- Market and limit order support

**Validation Layer** (`trading_bot/validators.py`):
- Input sanitization
- Symbol format checking
- Quantity/price validation
- Enum-based type safety

**Logging Configuration** (`trading_bot/logging_config.py`):
- File and console handlers
- Configurable log levels
- Timestamped log files

### 2. Error Handling

**Input Validation:**
```python
try:
    symbol = validate_symbol("BTC")  # Too short
except ValidationError as e:
    print(f"Validation Error: {e}")
```

**API Errors:**
```python
try:
    response = client.place_order(...)
except BinanceAPIError as e:
    logger.error(f"API Error: {e}")
```

**Missing Credentials:**
```python
if not api_key or not api_secret:
    raise ValueError("API credentials not found")
```

### 3. Logging Features

**Debug Level:**
- API request parameters
- API response body
- Function entry/exit

**Info Level:**
- Order placement events
- Successful operations
- Account actions

**Error Level:**
- API failures
- Validation errors
- Network issues

## Performance Notes

- **Order Placement:** < 1 second (typically 400-600ms)
- **Account Info Fetch:** < 1 second
- **Open Orders List:** < 1 second
- **Request Timeout:** 10 seconds (configurable)

## Troubleshooting

### Issue: "API credentials not found"
**Solution:**
```bash
# Verify environment variables are set
echo %BNB_API_KEY%   # Windows
echo $BNB_API_KEY    # Linux/macOS
```

### Issue: "Precision is over the maximum"
**Solution:** Use valid quantity for the symbol. Check Binance Futures documentation for symbol-specific limits.

### Issue: Order placed but status shows "REJECTED"
**Solution:** Check logs for specific error. Common causes:
- Insufficient balance
- Invalid quantity precision
- API key lacks "Trade" permission

### Issue: No log files created
**Solution:** Ensure `logs/` directory exists. The app creates it automatically, but check permissions.

## Next Steps

1. **Get Testnet Account:** [Binance Futures Testnet](https://testnet.binancefuture.com/)
2. **Generate API Credentials:** Account settings → API Management
3. **Set Environment Variables:** Copy your API key and secret
4. **Run Examples:** Start with `python cli.py --info`
5. **Place Test Orders:** Try market order first, then limit order
6. **Check Logs:** Review logs in `logs/` directory for details

---

**Last Updated:** 2024-01-15  
**Status:** Ready for testing
