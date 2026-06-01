"""Binance Futures API Client"""
import requests
import time
import hashlib
import hmac
from urllib.parse import urlencode
from typing import Dict, Optional, Any
from .logging_config import logger


class BinanceAPIError(Exception):
    """Binance API error"""
    pass


class BinanceFuturesClient:
    """Wrapper for Binance Futures API (Testnet)"""
    
    BASE_URL = "https://testnet.binancefuture.com"
    REQUEST_TIMEOUT = 10
    
    def __init__(self, api_key: str, api_secret: str):
        """Initialize Binance Futures client
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "trading-bot/1.0"
        })
        
        logger.info(f"Binance Futures Client initialized for testnet: {self.BASE_URL}")
    
    def _get_request_headers(self) -> Dict[str, str]:
        """Get headers with API key
        
        Returns:
            Headers dictionary
        """
        headers = self.session.headers.copy()
        headers["X-MBX-APIKEY"] = self.api_key
        return headers
    
    def _generate_signature(self, query_string: str) -> str:
        """Generate HMAC SHA256 signature
        
        Args:
            query_string: Query string to sign
            
        Returns:
            Signature hex string
        """
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _request(
        self,
        method: str,
        endpoint: str,
        signed: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to Binance API
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint path
            signed: Whether request needs signature
            **kwargs: Additional parameters
            
        Returns:
            Response JSON as dictionary
            
        Raises:
            BinanceAPIError: If API request fails
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        # Add timestamp for signed requests
        if signed:
            if "params" not in kwargs:
                kwargs["params"] = {}
            kwargs["params"]["timestamp"] = int(time.time() * 1000)
        
        params = kwargs.get("params", {})
        
        try:
            logger.debug(f"API Request: {method} {endpoint} | Params: {params}")
            
            # Sign request if needed
            if signed:
                query_string = urlencode(params)
                signature = self._generate_signature(query_string)
                params["signature"] = signature
            
            # Make request
            headers = self._get_request_headers()
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                timeout=self.REQUEST_TIMEOUT
            )
            
            logger.debug(f"API Response Status: {response.status_code}")
            
            # Check for errors
            if response.status_code >= 400:
                error_msg = response.text
                logger.error(f"API Error {response.status_code}: {error_msg}")
                raise BinanceAPIError(f"API Error {response.status_code}: {error_msg}")
            
            result = response.json()
            logger.debug(f"API Response: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            raise BinanceAPIError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            raise BinanceAPIError(error_msg)
    
    def check_server_time(self) -> int:
        """Check server time (for debugging)
        
        Returns:
            Server timestamp in milliseconds
        """
        result = self._request("GET", "/fapi/v1/time")
        return result.get("serverTime")
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information
        
        Returns:
            Account information dictionary
        """
        logger.info("Fetching account information...")
        return self._request("GET", "/fapi/v2/account", signed=True)
    
    def place_order(
        self,
        symbol: str,
        side: str,
        type_: str,
        quantity: float,
        price: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Place an order on Binance Futures
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            side: BUY or SELL
            type_: MARKET or LIMIT
            quantity: Order quantity
            price: Price (required for LIMIT orders)
            **kwargs: Additional parameters
            
        Returns:
            Order response dictionary
            
        Raises:
            BinanceAPIError: If order placement fails
        """
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": type_.upper(),
            "quantity": quantity,
            **kwargs
        }
        
        if type_.upper() == "LIMIT":
            if price is None:
                raise BinanceAPIError("Price is required for LIMIT orders")
            params["price"] = price
            params["timeInForce"] = "GTC"  # Good Till Cancelled
        
        logger.info(f"Placing {type_} order: {side} {quantity} {symbol} @ {price if price else 'market price'}")
        
        result = self._request("POST", "/fapi/v1/order", signed=True, params=params)
        
        logger.info(f"Order placed successfully: {result.get('orderId')}")
        return result
    
    def cancel_order(self, symbol: str, order_id: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """Cancel an order
        
        Args:
            symbol: Trading symbol
            order_id: Order ID to cancel
            **kwargs: Additional parameters
            
        Returns:
            Cancel response dictionary
        """
        params = {"symbol": symbol, **kwargs}
        
        if order_id is not None:
            params["orderId"] = order_id
        
        logger.info(f"Cancelling order {order_id} for {symbol}...")
        
        return self._request("DELETE", "/fapi/v1/order", signed=True, params=params)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """Get open orders
        
        Args:
            symbol: Optional specific symbol
            
        Returns:
            List of open orders
        """
        params = {}
        if symbol:
            params["symbol"] = symbol
        
        logger.info(f"Fetching open orders...")
        
        return self._request("GET", "/fapi/v1/openOrders", signed=True, params=params)
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Get order status
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
            
        Returns:
            Order status dictionary
        """
        params = {"symbol": symbol, "orderId": order_id}
        
        logger.debug(f"Fetching order status: {order_id}")
        
        return self._request("GET", "/fapi/v1/order", signed=True, params=params)
