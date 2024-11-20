"""Various helpers to assist in the use of fitout."""

from datetime import date, timedelta


# Date helpers
def todays_date():
    """
    Returns the current date.

    Returns:
        datetime.date: The current date.
    """
    return date.today()


def days_ago(n):
    """
    Calculate the date that is 'n' days before today.

    Args:
        n (int): The number of days to subtract from today's date.

    Returns:
        datetime.date: The date 'n' days before today.
    """
    return todays_date() - timedelta(days=n)


def dates_array(start_date, end_date):
    """
    Generate an array of dates from start_date to end_date.

    Args:
        start_date (datetime.date): The start date.
        end_date (datetime.date): The end date.

    Returns:
        list: A list of dates from start_date to end_date.
    """
    return [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]


# Data helpers
def number_precision(value, precision):
    """
    Rounds a number to a given precision.

    Args:
        value (float): The number to be rounded.
        precision (int): The number of decimal places to round to. If 0, the number is converted to an integer.

    Returns:
        float: The rounded number if precision is greater than 0.
        int: The integer value if precision is 0.
    """
    value = round(value, precision)
    if precision == 0:
        return int(value)
    return value


def fill_missing_with_neighbours(data_list):
    """
    Replaces missing values in a list with the average of the neighbouring values.

    Args:
        data_list (list): A list of data values, where some values may be None. 

    Returns:
        list: A list with missing values replaced by the average of the neighbouring values.
    """
    list_len = len(data_list)
    for i in range(1, list_len - 1):
        if data_list[i] is None:
            if i > 0 and i < list_len - 1:
                # Replace with average of neighbours, if they exist
                j = i + 1
                while j < list_len and data_list[j] is None:
                    j += 1
                if j < list_len:
                    data_list[i] = (data_list[i - 1] + data_list[j]) / 2.
                else:
                    data_list[i] = data_list[i - 1]
            elif i == 0:
                # Replace with next value, if at the beginning
                data_list[i] = data_list[i + 1]
            else:
                # Replace with previous value, if at the end
                data_list[i] = data_list[i - 1]
    return data_list


def fix_invalid_data_points(data_list, min_value, max_value):
    """
    Replaces out-of-range values in a list with the average of the neighbouring values.

    Args:
        data_list (list): A list of data values, where some values may be out of range. 

    Returns:
        list: A list with dubious values replaced by the average of the neighbouring values.
    """
    list_len = len(data_list)
    for i in range(1, list_len - 1):
        if data_list[i] < min_value or data_list[i] > max_value:
            if i > 0 and i < list_len - 1:
                # DEBUG: Catch the None values.
                if data_list[i - 1] is None or data_list[i + 1] is None:
                    print(f"None value at index {i + 1}")
                # Replace with average of neighbours, if they exist
                data_list[i] = (data_list[i - 1] + data_list[i + 1])/2.
            elif i == 0:
                # Replace with next value, if at the beginning
                data_list[i] = data_list[i + 1]
            else:
                # Replace with previous value, if at the end
                data_list[i] = data_list[i - 1]
    return data_list
