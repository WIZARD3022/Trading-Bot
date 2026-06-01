"""Input validation for trading bot"""
from enum import Enum
from typing import Tuple


class OrderSide(str, Enum):
    """Order side enumeration"""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order type enumeration"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_symbol(symbol: str) -> str:
    """Validate trading symbol format
    
    Args:
        symbol: Trading symbol (e.g., BTCUSDT)
        
    Returns:
        Validated symbol in uppercase
        
    Raises:
        ValidationError: If symbol format is invalid
    """
    symbol = symbol.upper().strip()
    
    if not symbol:
        raise ValidationError("Symbol cannot be empty")
    
    if len(symbol) < 6:
        raise ValidationError(f"Symbol '{symbol}' appears invalid (too short)")
    
    if not symbol.endswith(("USDT", "BUSD", "USDC")):
        raise ValidationError(f"Symbol '{symbol}' must end with USDT, BUSD, or USDC")
    
    return symbol


def validate_side(side: str) -> OrderSide:
    """Validate order side
    
    Args:
        side: Order side (BUY/SELL)
        
    Returns:
        OrderSide enum value
        
    Raises:
        ValidationError: If side is invalid
    """
    side = side.upper().strip()
    
    try:
        return OrderSide(side)
    except ValueError:
        raise ValidationError(f"Side must be BUY or SELL, got '{side}'")


def validate_order_type(order_type: str) -> OrderType:
    """Validate order type
    
    Args:
        order_type: Order type (MARKET/LIMIT)
        
    Returns:
        OrderType enum value
        
    Raises:
        ValidationError: If order type is invalid
    """
    order_type = order_type.upper().strip()
    
    try:
        return OrderType(order_type)
    except ValueError:
        raise ValidationError(f"Order type must be MARKET or LIMIT, got '{order_type}'")


def validate_quantity(quantity: str) -> float:
    """Validate order quantity
    
    Args:
        quantity: Order quantity as string
        
    Returns:
        Validated quantity as float
        
    Raises:
        ValidationError: If quantity is invalid
    """
    try:
        qty = float(quantity)
    except ValueError:
        raise ValidationError(f"Quantity must be a number, got '{quantity}'")
    
    if qty <= 0:
        raise ValidationError(f"Quantity must be greater than 0, got {qty}")
    
    if qty > 1000000:
        raise ValidationError(f"Quantity seems unreasonably large: {qty}")
    
    return qty


def validate_price(price: str) -> float:
    """Validate order price
    
    Args:
        price: Order price as string
        
    Returns:
        Validated price as float
        
    Raises:
        ValidationError: If price is invalid
    """
    try:
        p = float(price)
    except ValueError:
        raise ValidationError(f"Price must be a number, got '{price}'")
    
    if p <= 0:
        raise ValidationError(f"Price must be greater than 0, got {p}")
    
    if p > 10000000:
        raise ValidationError(f"Price seems unreasonably large: {p}")
    
    return p


def validate_order_params(
    symbol: str, 
    side: str, 
    order_type: str, 
    quantity: str,
    price: str = None
) -> Tuple[str, OrderSide, OrderType, float, float]:
    """Validate all order parameters together
    
    Args:
        symbol: Trading symbol
        side: Order side (BUY/SELL)
        order_type: Order type (MARKET/LIMIT)
        quantity: Order quantity
        price: Order price (required for LIMIT)
        
    Returns:
        Tuple of validated (symbol, side, order_type, quantity, price)
        
    Raises:
        ValidationError: If any parameter is invalid
    """
    validated_symbol = validate_symbol(symbol)
    validated_side = validate_side(side)
    validated_order_type = validate_order_type(order_type)
    validated_quantity = validate_quantity(quantity)
    
    validated_price = None
    if validated_order_type == OrderType.LIMIT:
        if price is None:
            raise ValidationError("Price is required for LIMIT orders")
        validated_price = validate_price(price)
    elif validated_order_type == OrderType.MARKET and price is not None:
        # Warn but don't fail if price provided for MARKET order
        validated_price = None
    
    return validated_symbol, validated_side, validated_order_type, validated_quantity, validated_price
