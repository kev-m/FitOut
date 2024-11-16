"""Classes to support importing FitBit data from different sources."""

from datetime import date, timedelta, datetime
import glob
import zipfile
from io import TextIOWrapper


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

    def _get_json_filename(self, data_path, current_date, date_increment_days=365):
        """
        Returns the actual JSON filename, based on the data path and the current date.

        Google Takeout data sometimes has a single file for a years worth of data, starting with a
        random day, possibly based on when the FitBit was activated. This method finds the correct
        file for the current date.

        Args:
            data_path (str): The path where the data files are stored.
            current_date (datetime.date): The current date for which the file name is to be generated.
            date_increment_days (int, optional): The number of days to increment when searching for the correct file. 
                                                 Defaults to 365.

        Returns:
            str: The actual file name.
        """
        files = self._get_json_file_list(data_path, current_date, date_increment_days)

        # Sort the files and find the one that is after the current_date
        files.sort()
        for file in files:
            file_date_str = file[-len('YYYY-mm-dd.json'):].split('.')[0]
            file_date = datetime.strptime(file_date_str, '%Y-%m-%d').date()
            if (current_date >= file_date) and (current_date < file_date + timedelta(days=date_increment_days)):
                return data_path + file_date_str + '.json'

        # If no file is found, return None or raise an error
        return None


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
            handle (obj): object that can be passed to csv.reader(f) or json.load(f).
        """
        return open(self.dir_path + file_path, 'r')

    def _get_json_file_list(self, data_path, current_date, date_increment_days=365):
        """
        Returns the actual JSON filename, based on the data path and the current date.

        Google Takeout data sometimes has a single file for a years worth of data, starting with a
        random day, possibly based on when the FitBit was activated. This method finds the correct
        file for the current date.

        Args:
            data_path (str): The path where the data files are stored.
            current_date (datetime.date): The current date for which the file name is to be generated.
            date_increment_days (int, optional): The number of days to increment when searching for the correct file. 
                                                 Defaults to 365.

        Returns:
            str: The actual file name.
        """

        # Find all JSON files that start with the year of the current_date
        pattern = self.dir_path + data_path + '*.json'
        files = glob.glob(pattern)

        return files


# Data source that can read files from a zip file
class ZipFileLoader(BaseFileLoader):
    """
    A class used to load data from files in a zip file.

    Attributes:
        file_path (str): The path to the root directory.
    Methods:
        open(str):
            Opens a file from the directory, returning a file object.
    """

    def __init__(self, dir_path):
        """
        Constructs all the necessary attributes for the ZipFileLoader object.

        Args:
            dir_path (str): The path to the zip source file.
        """
        self.dir_path = dir_path

        with zipfile.ZipFile(self.dir_path, 'r') as zip_ref:
            self.zip_files = zip_ref.namelist()  # Get a list of all files in the zip

    def open(self, file_path):
        """
        Loads data from the file and returns it.

        Args:
            file_path (str): The path to the file to be loaded.

        Returns:
            handle (obj): object that can be passed to csv.reader(f) or json.load(f).
        """
        with zipfile.ZipFile(self.dir_path, 'r') as zip_ref:
            try:
                return TextIOWrapper(zip_ref.open(file_path, 'r'), 'utf-8')
            except KeyError:
                raise FileNotFoundError(f"File {file_path} not found in zip file.")

    def _get_json_file_list(self, data_path, current_date, date_increment_days=365):
        """
        Returns the actual JSON filename, based on the data path and the current date.

        Google Takeout data sometimes has a single file for a years worth of data, starting with a
        random day, possibly based on when the FitBit was activated. This method finds the correct
        file for the current date.

        Args:
            data_path (str): The path where the data files are stored.
            current_date (datetime.date): The current date for which the file name is to be generated.
            date_increment_days (int, optional): The number of days to increment when searching for the correct file. 
                                                 Defaults to 365.

        Returns:
            str: The actual file name.
        """

        # Find all JSON files in the zip that start with the year of the current_date
        files = [f for f in self.zip_files if f.startswith(data_path) and f.endswith('.json')]   # Filter for JSON files
        files.sort()
        return files
