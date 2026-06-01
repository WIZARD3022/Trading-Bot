"""Order management and placement logic"""
from typing import Dict, Optional, Any
from .client import BinanceFuturesClient, BinanceAPIError
from .validators import OrderSide, OrderType, ValidationError
from .logging_config import logger


class OrderManager:
    """Manages order placement and tracking"""
    
    def __init__(self, client: BinanceFuturesClient):
        """Initialize order manager
        
        Args:
            client: BinanceFuturesClient instance
        """
        self.client = client
        logger.info("OrderManager initialized")
    
    def place_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float
    ) -> Dict[str, Any]:
        """Place a market order
        
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Order quantity
            
        Returns:
            Order response dictionary
            
        Raises:
            BinanceAPIError: If order fails
        """
        logger.info(f"Placing MARKET {side.value} order: {quantity} {symbol}")
        
        try:
            response = self.client.place_order(
                symbol=symbol,
                side=side.value,
                type_="MARKET",
                quantity=quantity
            )
            
            logger.info(f"MARKET order placed successfully: {self._format_order_response(response)}")
            return response
            
        except BinanceAPIError as e:
            logger.error(f"Failed to place MARKET order: {e}")
            raise
    
    def place_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        price: float
    ) -> Dict[str, Any]:
        """Place a limit order
        
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Order quantity
            price: Order price
            
        Returns:
            Order response dictionary
            
        Raises:
            BinanceAPIError: If order fails
        """
        logger.info(f"Placing LIMIT {side.value} order: {quantity} {symbol} @ {price}")
        
        try:
            response = self.client.place_order(
                symbol=symbol,
                side=side.value,
                type_="LIMIT",
                quantity=quantity,
                price=price
            )
            
            logger.info(f"LIMIT order placed successfully: {self._format_order_response(response)}")
            return response
            
        except BinanceAPIError as e:
            logger.error(f"Failed to place LIMIT order: {e}")
            raise
    
    def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Place an order (generic)
        
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            order_type: MARKET or LIMIT
            quantity: Order quantity
            price: Price (required for LIMIT)
            
        Returns:
            Order response dictionary
        """
        if order_type == OrderType.MARKET:
            return self.place_market_order(symbol, side, quantity)
        elif order_type == OrderType.LIMIT:
            if price is None:
                raise ValidationError("Price required for LIMIT orders")
            return self.place_limit_order(symbol, side, quantity, price)
        else:
            raise ValidationError(f"Unknown order type: {order_type}")
    
    @staticmethod
    def _format_order_response(response: Dict[str, Any]) -> str:
        """Format order response for logging
        
        Args:
            response: Order response dictionary
            
        Returns:
            Formatted string
        """
        order_id = response.get("orderId", "N/A")
        status = response.get("status", "N/A")
        executed_qty = response.get("executedQty", 0)
        avg_price = response.get("avgPrice", "N/A")
        
        return f"OrderID={order_id}, Status={status}, ExecutedQty={executed_qty}, AvgPrice={avg_price}"
    
    @staticmethod
    def format_order_display(response: Dict[str, Any]) -> str:
        """Format order response for display
        
        Args:
            response: Order response dictionary
            
        Returns:
            Formatted display string
        """
        lines = [
            "\n" + "=" * 60,
            "ORDER RESPONSE SUMMARY",
            "=" * 60,
            f"Order ID:        {response.get('orderId', 'N/A')}",
            f"Symbol:          {response.get('symbol', 'N/A')}",
            f"Side:            {response.get('side', 'N/A')}",
            f"Type:            {response.get('type', 'N/A')}",
            f"Status:          {response.get('status', 'N/A')}",
            f"Quantity:        {response.get('origQty', 'N/A')}",
            f"Executed Qty:    {response.get('executedQty', 'N/A')}",
            f"Price:           {response.get('price', 'N/A')}",
            f"Avg Price:       {response.get('avgPrice', 'N/A')}",
            f"Commission:      {response.get('commission', 'N/A')}",
            f"Commission Asset:{response.get('commissionAsset', 'N/A')}",
            f"Time:            {response.get('time', 'N/A')}",
            "=" * 60,
        ]
        
        return "\n".join(lines)
