"""A Python library to extract FitBit Google Takeout data."""
# Semantic Versioning according to https://semver.org/spec/v2.0.0.html
__version__ = "v0.0.4"  # Adding automatic detection of RHR JSON files

import csv
from datetime import date, timedelta, datetime
import json
import glob


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
    for i in range(1, len(data_list) - 1):
        if data_list[i] is None:
            if i > 0 and i < len(data_list) - 1:
                # Replace with average of neighbours, if they exist
                data_list[i] = (data_list[i - 1] + data_list[i + 1])/2.
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
    for i in range(1, len(data_list) - 1):
        if data_list[i] < min_value or data_list[i] > max_value:
            if i > 0 and i < len(data_list) - 1:
                # Replace with average of neighbours, if they exist
                data_list[i] = (data_list[i - 1] + data_list[i + 1])/2.
            elif i == 0:
                # Replace with next value, if at the beginning
                data_list[i] = data_list[i + 1]
            else:
                # Replace with previous value, if at the end
                data_list[i] = data_list[i - 1]
    return data_list


# Data loading classes
# Abstract base class for data loaders
class BaseFileLoader():
    """
    Abstract class used to handle different data file sources.
    Methods:
        open(str):
            Opens a file from the data source, returning a file object.
    """

    def open(self):
        """
        Opens a file from the data source and returns a file handle.
        """
        pass

    def _get_json_filename(self, data_path, current_date):
        """
        Returns the actual JSON filename, based on the data path and the current date.

        Google Takeout data sometimes has a single file for a years worth of data, starting with a
        random day, possibly based on when the FitBit was activated. This method finds the correct
        file for the current date.

        Args:
            current_date (datetime.date): The current date for which the file name is to be generated.

        Returns:
            str: The actual file name.
        """
        pass


# Data source that can read files from a directory
class NativeFileLoader(BaseFileLoader):
    """
    A class used to load data from files in a directory structure.
    Attributes:
        file_path (str): The path to the root directory.
    Methods:
        open(str):
            Opens a file from the directory, returning a file object.
    """

    def __init__(self, dir_path):
        """
        Constructs all the necessary attributes for the NativeFileLoader object.

        Args:
            dir_path (str): The path to the top level directory.
        """
        self.dir_path = dir_path

    def open(self, file_path):
        """
        Loads data from the file and returns it.

        Args:
            file_path (str): The path to the file to be loaded.

        Returns:
            str: The data loaded from the file.
        """
        return open(self.dir_path + file_path, 'r')

    def get_json_filename(self, data_path, current_date):
        """
        Returns the actual JSON filename, based on the data path and the current date.

        Google Takeout data sometimes has a single file for a years worth of data, starting with a
        random day, possibly based on when the FitBit was activated. This method finds the correct
        file for the current date.

        Args:
            current_date (datetime.date): The current date for which the file name is to be generated.

        Returns:
            str: The actual file name.
        """

        # Find all JSON files that start with the year of the current_date
        pattern = self.dir_path + data_path + '*.json'
        files = glob.glob(pattern)

        # Sort the files and find the one that is after the current_date
        files.sort()
        for file in files:
            file_date_str = file[-len('YYYY-mm-dd.json'):].split('.')[0]
            file_date = datetime.strptime(file_date_str, '%Y-%m-%d').date()
            if (current_date >= file_date) and (current_date < file_date + timedelta(days=365)):
                return data_path + file_date_str + '.json'

        # If no file is found, return None or raise an error
        return None


# Data processing classes

# Base CSV reader
class BasicCSVImporter:
    """
    A class used to import data from a CSV file.
    Attributes:
        data_source (BaseFileLoader): The data source object used to open files.
        data_path (str): The path to the directory containing the CSV files.
        precision (int): The precision for numerical data (default is 0).
    Methods:
        read_csv(file_path):
            Reads a CSV file and returns the columns and data.
    """

    def __init__(self, data_source, data_path, precision=0):
        """
        Constructs all the necessary attributes for the BasicCSVImporter object.
        Args:
            data_path (str): The path to the directory containing the CSV files.
            precision (int): The precision for numerical data (default is 0).
        """
        self.data_source = data_source
        self.data_path = data_path
        self.precision = precision

    def read_csv(self, file_path):
        """
        Reads a CSV file and returns its columns and data.

        Args:
            file_path (str): The path to the CSV file.

        Returns:
            tuple: A tuple containing two elements:
            - cols (list): A list of column names.
            - data (list): A list of rows, where each row is a list of values.
        """
        with self.data_source.open(file_path) as f:
            reader = csv.reader(f)
            rows = list(reader)
            cols = rows[0]
            data = rows[1:]
        return cols, data


# Specialised CSV reader that handles CSV files with only 2 lines of data
class TwoLineCSVImporter(BasicCSVImporter):
    """
    A CSV importer that processes data from CSV files with two lines of data.
    Methods:
        get_data(start_date, end_date):
            Retrieves data for a range of dates from start_date to end_date.
        get_data_for_date(current_date):
            Retrieves data for a specific date.
    Attributes:
        data (list): A list to store the data for each date.
        dates (list): A list to store the dates corresponding to the data.
    """

    def get_data(self, start_date=days_ago(10), end_date=todays_date()):
        """
        Retrieves data for a range of dates from start_date to end_date.
        Args:
            start_date (datetime.date, optional): The start date for data retrieval. Defaults to 10 days ago.
            end_date (datetime.date, optional): The end date for data retrieval. Defaults to today's date.
        Returns:
            list: A list of data for each date in the specified range.
        """
        num_days = (end_date - start_date).days + 1
        self.data = [None] * num_days
        self.dates = [None] * num_days
        current_date = start_date
        index = 0
        while current_date <= end_date:
            self.data[index] = self.get_data_for_date(current_date)
            self.dates[index] = current_date
            current_date += timedelta(days=1)
            index += 1
        return self.data

    def get_data_for_date(self, current_date):
        """
        Retrieves data for a specific date.
        Args:
            current_date (datetime.date): The date for which to retrieve data.
        Returns:
            float or None: The data for the specified date, or None if the file is not found.
        """
        file_name = self._get_dailydata_filename(current_date)
        try:
            cols, rows = self.read_csv(self.data_path + file_name)
            data = number_precision(float(rows[0][1]), self.precision)
        except FileNotFoundError:
            data = None
        return data

    def _get_dailydata_filename(self, current_date):
        """
        Generates a file name used to load data, based on the given date.

        This abstract method must be implemented by subclasses.

        Args:
            current_date (datetime.date): The current date for which the file name is to be generated.

        Returns:
            str: The generated file name.
        """
        pass


# Importers for specific Fitbit data types

# Importer for overnight breathing rate data
class BreathingRate(TwoLineCSVImporter):
    """
    Importer for daily breathing rate data.

    The respiratory rate (or breathing rate) is the rate at which breathing occurs. This is usually measured in breaths per minute.

    The "Daily Respiration Rate Summary" files include daily granularity recordings of your Respiratory Rate during a sleep. The description is as follows:

    daily_respiratory_rate: Breathing rate average estimated from deep sleep when possible, and from light sleep when deep sleep data is not available.
    """

    def __init__(self, data_source, precision=0):
        """
        Constructs the nightly Breathing Rate class instance.

        Args:
            data_source (BaseFileLoader): The data source used to load data.
            precision (int): The precision for numerical data (default is 0).
        """
        # C:\Dev\Fitbit\Google\Takeout\Fitbit\Heart Rate Variability\Daily Respiratory Rate Summary - 2024-07-22.csv
        super().__init__(data_source,
                         '/Fitbit/Heart Rate Variability/Daily Respiratory Rate Summary - ', precision)
        self.data = {}

    def _get_dailydata_filename(self, current_date):
        """
        Generates a file name based on the given date.

        Args:
            current_date (datetime): The current date for which the file name is to be generated.

        Returns:
            str: The generated file name in the format 'YYYY-MM-DD.csv'.
        """
        return current_date.strftime('%Y-%m-%d') + '.csv'


# Importer for overnight heart rate variability data
class HeartRateVariability(TwoLineCSVImporter):
    """
    Importer for daily heart rate variability data.

    Heart rate variability (HRV) is the physiological phenomenon of variation in the time interval between heartbeats. It is measured by the variation in the beat-to-beat interval.

    The "Daily Heart Rate Variability Summary" files include daily granularity recordings of your HRV during a sleep. The description for the values of each row is as follows:

    rmssd: Root mean squared value of the successive differences of time interval between successive heart beats., measured during sleep.
    nremhr:  Heart rate measured during non-REM sleep (i.e. light and deep sleep stages).
    entropy:  Entropy quantifies randomness or disorder in a system. High entropy indicates high HRV. Entropy is measured from the histogram of time interval between successive heart beats values measured during sleep.
    """

    def __init__(self, data_source, precision=0):
        """
        Constructs the nightly Heart Rate Variability class instance.

        Args:
            data_source (BaseFileLoader): The data source used to load data.
            precision (int): The precision for numerical data (default is 0).
        """
        # C:\Dev\Fitbit\Google\Takeout\Fitbit\Heart Rate Variability\Daily Heart Rate Variability Summary - 2024-07-(21).csv
        # timestamp,rmssd,nremhr,entropy
        # 2024-07-21T00:00:00,29.232,49.623,2.472
        super().__init__(data_source,
                         '/Fitbit/Heart Rate Variability/Daily Heart Rate Variability Summary - ')
        self.data = {}

    def _get_dailydata_filename(self, current_date):
        """
        Generates a file name based on the given date.

        If the given date is the first day of the month, the file name will be in the format 'YYYY-MM-.csv'.
        Otherwise, the file name will be in the format 'YYYY-MM-(D-1).csv', where D is the day of the given date.

        Args:
            current_date (datetime.date): The date for which to generate the file name.

        Returns:
            str: The generated file name.
        """
        if current_date.day == 1:
            return current_date.strftime('%Y-%m-') + '.csv'
        return current_date.strftime('%Y-%m-(') + str(current_date.day-1) + ').csv'


# Importer for overnight resting heart rate data
class RestingHeartRate():
    """
    Importer for daily resting heart rate data.
    """

    def __init__(self, data_source, precision=0):
        """
        Constructs the nightly Resting Heart Rate class instance.

        Args:
            data_source (BaseFileLoader): The data source used to load data.
            precision (int): The precision for numerical data (default is 0).
            hint (str): The hint for the date format in the file name (default is '%Y-03-01').
        """
        # C:\Dev\Fitbit\Google\Takeout\Fitbit\Global Export Data\resting_heart_rate-2024-03-01.json
        # [{
        #   "dateTime" : "03/01/24 00:00:00",
        #   "value" : {
        #     "date" : "03/01/24",
        #     "value" : 53.01231098175049,
        #     "error" : 6.787087440490723
        #   }
        # },
        # ...
        #
        self.precision = precision
        self.data_source = data_source
        self.data_path = '/Fitbit/Global Export Data/'
        self.data_file = 'resting_heart_rate-'

    def get_data(self, start_date=days_ago(10), end_date=todays_date()):
        """
        Retrieves data for a range of dates from start_date to end_date.
        Args:
            start_date (datetime.date, optional): The start date for data retrieval. Defaults to 10 days ago.
            end_date (datetime.date, optional): The end date for data retrieval. Defaults to today's date.
        Returns:
            list (int): The overnight resting heart rate in the specified range.
        """
        num_days = (end_date - start_date).days + 1
        self.data = [None] * num_days
        self.dates = [None] * num_days
        current_date = start_date
        index = 0

        while index < num_days:
            json_filename = self.data_source.get_json_filename(
                self.data_path + self.data_file, current_date)
            with self.data_source.open(json_filename) as f:
                json_data = json.load(f)
            for json_entry in json_data:
                json_date = json_entry['value']['date']
                if index > 0 and json_date is None:
                    # We've run out of data in the data file, return what we have
                    return self.data
                json_value = json_entry['value']['value']
                if json_date == current_date.strftime('%m/%d/%y'):
                    self.data[index] = number_precision(
                        json_value, self.precision)
                    self.dates[index] = current_date
                    index += 1
                    current_date += timedelta(days=1)
                if index == num_days:
                    break
            # TODO: Handle missing data and errors

        return self.data
