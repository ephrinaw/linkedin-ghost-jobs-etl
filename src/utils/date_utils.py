import re
from datetime import datetime, date, timedelta

def parse_relative_date(relative_str: str) -> date:
    """Convert relative date string to date object"""
    if not relative_str or not isinstance(relative_str, str):
        return None
    
    today = date.today()
    relative_str = relative_str.lower()
    
    # Handle cases like "Posted 3 days ago"
    numbers = re.findall(r'\d+', relative_str)
    
    if not numbers:
        if 'today' in relative_str or 'just now' in relative_str:
            return today
        elif 'yesterday' in relative_str:
            return today - timedelta(days=1)
        else:
            return None
    
    num = int(numbers[0])
    
    if 'hour' in relative_str or 'minute' in relative_str:
        return today
    elif 'day' in relative_str:
        return today - timedelta(days=num)
    elif 'week' in relative_str:
        return today - timedelta(weeks=num)
    elif 'month' in relative_str:
        return today - timedelta(days=30 * num)  # Approximation
    else:
        return None

def format_date_for_db(date_obj):
    """Format date for database storage"""
    if isinstance(date_obj, date):
        return date_obj.isoformat()
    return date_obj