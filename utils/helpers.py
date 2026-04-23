"""
General utility functions.
"""

from datetime import datetime
from config.settings import DATE_FORMAT, DISPLAY_DATE_FORMAT


def calculate_nights(depart_date: str, return_date: str) -> int:
    """
    Calculate number of nights between two dates.
    
    Args:
        depart_date: Departure date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD)
    
    Returns:
        Number of nights
    """
    try:
        depart = datetime.strptime(depart_date, DATE_FORMAT)
        return_dt = datetime.strptime(return_date, DATE_FORMAT)
        return (return_dt - depart).days
    except:
        return 1


def format_currency(amount: int) -> str:
    """
    Format amount as USD currency.
    
    Args:
        amount: Amount in USD
    
    Returns:
        Formatted string like "$1,500"
    """
    return f"${amount:,}"


def format_date(date_str: str, output_format: str = DISPLAY_DATE_FORMAT) -> str:
    """
    Format date string for display.
    
    Args:
        date_str: Date string (YYYY-MM-DD)
        output_format: Desired output format
    
    Returns:
        Formatted date string
    """
    try:
        date_obj = datetime.strptime(date_str, DATE_FORMAT)
        return date_obj.strftime(output_format)
    except:
        return date_str