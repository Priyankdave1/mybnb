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
        date = datetime.strptime(date_str, '%Y-%m-%d')
        if(date<datetime.today()):
            return False
        return True
    except ValueError:
        return False

def not_in_future(date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d')
    if(date<datetime.today()):
        return False
    return True

def is_over_18(date_of_birth):
    # Convert the date string to a datetime object
    dob = datetime.strptime(date_of_birth, '%Y-%m-%d')

    # Get the current date
    current_date = datetime.now()

    # Calculate the age by subtracting the birth year from the current year
    age = current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))

    # Check if the age is greater than or equal to 18
    return age >= 18

def get_number_of_days_between(start_date, end_date):
    delta = end_date - start_date
    return delta.days + 1
def todays_date():
    return datetime.today().strftime('%Y-%m-%d')