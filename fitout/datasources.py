"""Classes to support importing FitBit data from different sources."""

from datetime import date, timedelta, datetime
import glob


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

    def get_json_filename(self, data_path, current_date, date_increment_days=365):
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
            if (current_date >= file_date) and (current_date < file_date + timedelta(days=date_increment_days)):
                return data_path + file_date_str + '.json'

        # If no file is found, return None or raise an error
        return None
