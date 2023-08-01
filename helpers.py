from datetime import datetime

def is_float(value):
    try:
        float_value = float(value)
        return True
    except ValueError:
        return False

def is_valid_latitude(latitude):
    if not is_float(latitude):
        return False
    latitude = float(latitude)
    return -90 <= latitude <= 90

def is_valid_longitude(longitude):
    if not is_float(longitude):
        return False
    longitude = float(longitude)
    return -180 <= longitude <= 180

def is_valid_date(date_str):
    try:
        # Check if the input date string can be parsed into a valid date using the 'YYYY-MM-DD' format
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False