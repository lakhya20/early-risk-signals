from typing import Any, List, Dict
from fastapi import HTTPException
from backend.core.logger import logger


def paginate(items: List[Any], page: int = 1, size: int = 10) -> Dict[str, Any]:
    """
    Paginate a list of items.
    
    Args:
        items: List of items to paginate
        page: Page number (1-indexed)
        size: Items per page
        
    Returns:
        Dictionary with paginated data and metadata
    """
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if size < 1:
        raise HTTPException(status_code=400, detail="Size must be >= 1")
    if size > 100:
        logger.warning(f"Page size {size} exceeds maximum, clamping to 100")
        size = 100
    
    total = len(items)
    start = (page - 1) * size
    end = start + size
    
    paginated_items = items[start:end]
    
    return {
        "items": paginated_items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size if total > 0 else 0
    }


def validate_customer_id(customer_id: str) -> str:
    """
    Validate customer ID format.
    
    Args:
        customer_id: Customer ID to validate
        
    Returns:
        Validated customer ID
        
    Raises:
        HTTPException: If customer ID is invalid
    """
    if not customer_id or not isinstance(customer_id, str):
        raise HTTPException(status_code=400, detail="Customer ID must be a non-empty string")
    
    customer_id = customer_id.strip()
    
    if len(customer_id) > 50:
        raise HTTPException(status_code=400, detail="Customer ID must be 50 characters or less")
    
    if not customer_id:
        raise HTTPException(status_code=400, detail="Customer ID cannot be empty")
    
    return customer_id


def handle_database_error(error: Exception, operation: str = "database operation") -> HTTPException:
    """
    Convert database errors to appropriate HTTP exceptions.
    
    Args:
        error: The database error
        operation: Description of the operation that failed
        
    Returns:
        HTTPException with appropriate status code and message
    """
    error_msg = str(error)
    logger.error(f"{operation} failed: {error_msg}", exc_info=True)
    
    # Handle specific database errors
    if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
        return HTTPException(status_code=404, detail=f"Resource not found: {error_msg}")
    
    if "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
        return HTTPException(status_code=409, detail=f"Resource already exists: {error_msg}")
    
    if "constraint" in error_msg.lower() or "foreign key" in error_msg.lower():
        return HTTPException(status_code=400, detail=f"Invalid data: {error_msg}")
    
    # Generic database error
    return HTTPException(status_code=500, detail=f"Database error during {operation}")
