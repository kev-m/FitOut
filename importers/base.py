"""A Python library to extract FitBit Google Takeout data."""

import csv
from datetime import timedelta

from fitout.helpers import days_ago, todays_date, number_precision


# Data processing classes
# Base importer class
class BaseImporter:
    """
    Abstract base class for data importers.

    Attributes:
        data_source (BaseFileLoader): The data source object used to open files.
        data_path (str): The path to the directory containing the data files.
        precision (int): The precision for numerical data (default is 0).
    Methods:
        get_data(start_date, end_date):
            Retrieves data for a range of dates from start_date to end_date.
    """

    def __init__(self, data_source, data_path, precision=0):
        """
        Constructs all the necessary attributes for the BaseImporter object.

        Args:
            data_source (BaseFileLoader): The data source object used to open files.
            data_path (str): The path to the directory containing the data files.
            precision (int): The precision for numerical data (default is 0).
        """
        self.data_source = data_source
        self.data_path = data_path
        self.precision = precision

    def get_data(self, start_date=days_ago(10), end_date=todays_date()):
        """
        Retrieves data for a range of dates from start_date to end_date.

        This abstract method must be implemented by subclasses.

        Args:
            start_date (datetime.date): The start date for data retrieval.
            end_date (datetime.date): The end date for data retrieval.

        Returns:
            list: A list of data for each date in the specified range.
        """
        pass


# Base CSV reader
class BasicCSVImporter(BaseImporter):
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


