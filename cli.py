#!/usr/bin/env python3
"""CLI entry point for the Trading Bot"""
import argparse
import sys
import os
from typing import Optional

from trading_bot.client import BinanceFuturesClient, BinanceAPIError
from trading_bot.orders import OrderManager
from trading_bot.validators import validate_order_params, ValidationError
from trading_bot.logging_config import logger


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser
    
    Returns:
        ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Binance Futures Trading Bot - Place orders on testnet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Place a market buy order
  python cli.py -s BTCUSDT -sd BUY -t MARKET -q 0.001

  # Place a limit sell order
  python cli.py -s ETHUSDT -sd SELL -t LIMIT -q 1.0 -p 2000.50

  # Get account info
  python cli.py --info
        """
    )
    
    parser.add_argument(
        "--api-key",
        required=False,
        help="Binance API Key (or set BNB_API_KEY env var)"
    )
    parser.add_argument(
        "--api-secret",
        required=False,
        help="Binance API Secret (or set BNB_API_SECRET env var)"
    )
    
    # Order placement arguments
    parser.add_argument(
        "-s", "--symbol",
        help="Trading symbol (e.g., BTCUSDT, ETHUSDT)"
    )
    parser.add_argument(
        "-sd", "--side",
        help="Order side: BUY or SELL"
    )
    parser.add_argument(
        "-t", "--type",
        dest="order_type",
        help="Order type: MARKET or LIMIT"
    )
    parser.add_argument(
        "-q", "--quantity",
        help="Order quantity"
    )
    parser.add_argument(
        "-p", "--price",
        help="Order price (required for LIMIT orders)"
    )
    
    # Info arguments
    parser.add_argument(
        "--info",
        action="store_true",
        help="Get account information"
    )
    parser.add_argument(
        "--open-orders",
        action="store_true",
        help="List open orders"
    )
    parser.add_argument(
        "--server-time",
        action="store_true",
        help="Check server time"
    )
    
    return parser


def get_api_credentials() -> tuple[str, str]:
    """Get API credentials from arguments or environment
    
    Returns:
        Tuple of (api_key, api_secret)
        
    Raises:
        ValueError: If credentials not found
    """
    # Try to get from environment first
    api_key = os.getenv("BNB_API_KEY")
    api_secret = os.getenv("BNB_API_SECRET")
    
    if not api_key or not api_secret:
        raise ValueError(
            "API credentials not found. Please set BNB_API_KEY and "
            "BNB_API_SECRET environment variables or provide --api-key and --api-secret"
        )
    
    return api_key, api_secret


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Check if any action is requested
    if not any([
        args.symbol, args.info, args.open_orders, args.server_time
    ]):
        parser.print_help()
        sys.exit(1)
    
    try:
        # Get API credentials
        api_key, api_secret = get_api_credentials()
        
        # Initialize client
        client = BinanceFuturesClient(api_key, api_secret)
        
        # Check server time
        if args.server_time:
            logger.info("Checking server time...")
            server_time = client.check_server_time()
            print(f"\n✓ Server Time: {server_time}")
            return 0
        
        # Get account info
        if args.info:
            logger.info("Fetching account information...")
            account = client.get_account_info()
            print_account_info(account)
            return 0
        
        # List open orders
        if args.open_orders:
            logger.info("Fetching open orders...")
            orders = client.get_open_orders()
            print_open_orders(orders)
            return 0
        
        # Place order
        if args.symbol:
            if not all([args.side, args.order_type, args.quantity]):
                print("ERROR: --symbol requires --side, --type, and --quantity")
                return 1
            
            # Validate inputs
            symbol, side, order_type, quantity, price = validate_order_params(
                symbol=args.symbol,
                side=args.side,
                order_type=args.order_type,
                quantity=args.quantity,
                price=args.price
            )
            
            # Print order request summary
            print_order_request(symbol, side, order_type, quantity, price)
            
            # Place order
            order_manager = OrderManager(client)
            response = order_manager.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price
            )
            
            # Print response
            print(order_manager.format_order_display(response))
            print("✓ Order placed successfully!")
            
            return 0
    
    except ValidationError as e:
        print(f"\n✗ Validation Error: {e}")
        return 1
    except BinanceAPIError as e:
        print(f"\n✗ API Error: {e}")
        return 1
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        return 1
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"\n✗ Unexpected Error: {e}")
        return 1


def print_order_request(symbol: str, side, order_type, quantity: float, price: Optional[float]):
    """Print order request summary
    
    Args:
        symbol: Trading symbol
        side: Order side
        order_type: Order type
        quantity: Order quantity
        price: Order price
    """
    print("\n" + "=" * 60)
    print("ORDER REQUEST SUMMARY")
    print("=" * 60)
    print(f"Symbol:      {symbol}")
    print(f"Side:        {side.value}")
    print(f"Type:        {order_type.value}")
    print(f"Quantity:    {quantity}")
    if price:
        print(f"Price:       {price}")
    print("=" * 60 + "\n")


def print_account_info(account: dict):
    """Print account information
    
    Args:
        account: Account information dictionary
    """
    print("\n" + "=" * 60)
    print("ACCOUNT INFORMATION")
    print("=" * 60)
    
    assets = account.get("assets", [])
    print(f"Total Assets: {len(assets)}")
    print("\nBalances (non-zero):")
    
    for asset in assets:
        free = float(asset.get("availableBalance", 0))
        locked = float(asset.get("walletBalance", 0)) - free
        
        if free > 0 or locked > 0:
            print(f"  {asset.get('asset')}: Available={free:.8f}, Locked={locked:.8f}")
    
    print("=" * 60)


def print_open_orders(orders: list):
    """Print open orders
    
    Args:
        orders: List of open orders
    """
    print("\n" + "=" * 60)
    print("OPEN ORDERS")
    print("=" * 60)
    
    if not orders:
        print("No open orders found.")
    else:
        print(f"Total Open Orders: {len(orders)}\n")
        
        for order in orders:
            print(f"Order ID: {order.get('orderId')}")
            print(f"  Symbol: {order.get('symbol')}")
            print(f"  Side: {order.get('side')}")
            print(f"  Type: {order.get('type')}")
            print(f"  Quantity: {order.get('origQty')}")
            print(f"  Price: {order.get('price')}")
            print(f"  Status: {order.get('status')}")
            print()
    
    print("=" * 60)


if __name__ == "__main__":
    sys.exit(main())
