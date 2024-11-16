"""A Python library to extract FitBit Google Takeout data."""

import csv
from datetime import timedelta, time, datetime
import json

from .helpers import days_ago, todays_date, number_precision


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
                         'Takeout/Fitbit/Heart Rate Variability/Daily Respiratory Rate Summary - ', precision)
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

    Heart rate variability (HRV) is the physiological phenomenon of variation in the time interval between heartbeats. 
    It is measured by the variation in the beat-to-beat interval.

    The "Daily Heart Rate Variability Summary" files include daily granularity recordings of your HRV during a sleep. 
    The description for the values of each row is as follows:

        rmssd: Root mean squared value of the successive differences of time interval between successive heart beats, 
            measured during sleep.
        nremhr:  Heart rate measured during non-REM sleep (i.e. light and deep sleep stages).
        entropy:  Entropy quantifies randomness or disorder in a system. High entropy indicates high HRV. Entropy 
            is measured from the histogram of time interval between successive heart beats values measured during sleep.
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
                         'Takeout/Fitbit/Heart Rate Variability/Daily Heart Rate Variability Summary - ')

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
class RestingHeartRate(BaseImporter):
    """
    Importer for daily resting heart rate data.
    """

    def __init__(self, data_source, precision=0):
        """
        Constructs the nightly Resting Heart Rate class instance.

        Args:
            data_source (BaseFileLoader): The data source used to load data.
            precision (int): The precision for numerical data (default is 0).
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
        super().__init__(data_source, 'Takeout/Fitbit/Global Export Data/', precision)
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
            json_filename = self.data_source._get_json_filename(
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


class BasicSleepInfo(BaseImporter):
    """
    Importer for basic overnight sleep data.
    """

    def __init__(self, data_source, precision=0, sleep_time=time(22, 0, 0), wake_time=time(6, 0, 0)):
        """
        Constructs the nightly sleep information importer instance.

        Sleep events during the day, i.e. after wake_time but before sleep_time, are excluded. 

        Args:
            data_source (BaseFileLoader): The data source used to load data.
            precision (int): The precision for numerical data (default is 0).
            sleep_time (datetime.time): The time to consider as the start of sleep (default is 22:00).
            wake_time (datetime.time): The time to consider as the end of sleep (default is 06:00).
        """
        # C:\Dev\Fitbit\Google\Takeout\Fitbit\Global Export Data\sleep-2022-03-02.json
        # C:\Dev\Fitbit\Google\Takeout\Fitbit\Global Export Data\sleep-2022-04-01.json
        # ...
        # C:\Dev\Fitbit\Google\Takeout\Fitbit\Global Export Data\sleep-2024-10-17.json
        # Each file spans one month (30 days) of sleep data, in reverse chronological order.
        # [{
        #   "logId" : 44940631937,
        #   "dateOfSleep" : "2024-03-21",
        #   "startTime" : "2024-03-20T22:04:00.000",
        #   "endTime" : "2024-03-21T06:55:30.000",
        #   "duration" : 31860000,
        #   "minutesToFallAsleep" : 5,
        #   "minutesAsleep" : 474,
        #   "minutesAwake" : 57,
        #   "minutesAfterWakeup" : 1,
        #   "timeInBed" : 531,
        #   "efficiency" : 96,
        #   "type" : "stages",
        #   "infoCode" : 0,
        #   "logType" : "manual",
        #   "levels" : {
        #      <out of scope>
        #   },
        #   "mainSleep" : true
        # },{
        #   .....
        #
        super().__init__(data_source, 'Takeout/Fitbit/Global Export Data/', precision)
        self.data_file = 'sleep-'
        self.sleep_time = sleep_time
        self.wake_time = wake_time

    def get_data(self, start_date=days_ago(10), end_date=todays_date()):
        """
        Retrieves data for a range of dates from start_date to end_date.

        This function parses the sleep data from the Fitbit Google Takeout data files and returns a partially processed
        result. At most one entry is created per day, even if there are multiple sleep entries in the data file.

        When a sleep entry is not the main sleep, the endTime is updated, the minutesAwake is incremented with the
        time between the last endTime and the current startTime, and the following dictionary entries are 
        incremented with the additional sleep values:
            `minutesAwake`, `summary_deep_mins`, `summary_wake_mins`, `summary_light_mins`, `summary_rem_mins`.



        Args:
            start_date (datetime.date, optional): The start date for data retrieval. Defaults to 10 days ago.
            end_date (datetime.date, optional): The end date for data retrieval. Defaults to today's date.
        Returns:
            dict: A dictionary containing the sleep data with the following structure:
                {
                'dateOfSleep': [list of dates (string)],
                'startTime': [list of start times (string)],
                'endTime': [list of end times (string)],
                'minutesToFallAsleep': [list of minutes to fall asleep (int)],
                'minutesAsleep': [list of minutes asleep (int)],
                'minutesAwake': [list of minutes awake (int)],
                'minutesAfterWakeup': [list of minutes after wakeup (int)],
                'timeInBed': [list of time in bed (int)],
                'efficiency': [list of efficiency (int)],
                'summary_deep_mins': [list of deep sleep minutes (int)],
                'summary_wake_mins': [list of wake minutes (int)],
                'summary_light_mins': [list of light sleep minutes (int)],
                'summary_rem_mins': [list of REM sleep minutes (int)]
                }

        """
        end_date += timedelta(
            days=1)  # Include the end date, to get the last night's sleep.
        num_days = (end_date - start_date).days + 1
        self.data_keys = ["dateOfSleep", "startTime", "endTime", "minutesToFallAsleep",
                          "minutesAsleep", "minutesAwake", "minutesAfterWakeup", "timeInBed",
                          "efficiency"]
        self.data = {key: [None] * num_days for key in self.data_keys}
        self.levels_summary_keys = ["deep", "wake", "light", "rem"]
        for key in self.levels_summary_keys:
            self.data[f"summary_{key}_mins"] = [None] * num_days

        current_date = start_date
        index = 0
        last_file = None

        while index < num_days:
            json_filename = self.data_source._get_json_filename(self.data_path + self.data_file, current_date, 30)
            if json_filename == last_file:
                # We've run out of data in the data files, return what we have
                log("No more data for", current_date, json_filename)
                return self.data
            last_file = json_filename
            with self.data_source.open(json_filename) as f:
                json_data = json.load(f)
                last_json_date = None
                for json_entry in reversed(json_data):
                    json_date_str = json_entry['dateOfSleep']
                    if index > 0 and json_date_str is None:
                        return self.data

                    json_date = datetime.strptime(json_date_str, '%Y-%m-%d').date()

                    # Catch up to the current or start date
                    if json_date < current_date:
                        continue

                    # Things get complicated here. We need to handle when there are multiple sleep entries in a day.
                    # The index should only get incremented when the current date is different from the last date.
                    while json_date > current_date:
                        index += 1
                        current_date += timedelta(days=1)
                        if index == num_days:
                            return self.data

                    if json_date == current_date:
                        # Check if the sleep entry is within the sleep time range
                        parts = json_entry['startTime'].split('T')
                        json_start_date = parts[0]
                        json_start_time = parts[1]
                        start_time = time.fromisoformat(json_start_time)

                        parts = json_entry['endTime'].split('T')
                        json_end_date = parts[0]
                        json_end_time = parts[1]
                        end_time = time.fromisoformat(json_end_time)

                        if (json_start_date == json_end_date) and (start_time > self.wake_time) and (end_time < self.sleep_time):
                            # Skip this sleep entry, it's not overnight
                            # log(json_entry)
                            log("Nap detected, skipping", json_start_date, json_start_time, json_end_time)
                            continue

                        if last_json_date != json_date_str:
                            # For the first sleep, capture all details
                            for key in self.data_keys:
                                self.data[key][index] = json_entry.get(key, None)
                            # Capture the summary levels
                            for key in self.levels_summary_keys:
                                summary = json_entry['levels']['summary']
                                if key in summary:
                                    self.data[f"summary_{key}_mins"][index] = summary[key]['minutes']

                        else:
                            # If the current date is the same as the last date, we need to update the endTime and minutesAwake
                            # of the main sleep entry.
                            # self.data[key][index]
                            # log(json_entry)
                            log("Non-main sleep detected, updating main sleep",
                                json_start_date, json_start_time, json_end_time)
                            # Increment the minutesAwake of the main sleep with the minutesAwake of the non-main sleep
                            self.data["minutesAwake"][index] += json_entry.get("minutesAwake", 0)
                            # Increment the minutesAwake of the main sleep with the minutesAwake of the non-main sleep
                            self.data["timeInBed"][index] += json_entry.get("timeInBed", 0)
                            # Increment the minutesAwake of the main sleep with the minutes between the last endTime and the current startTime
                            last_wake_time = datetime.strptime(self.data["endTime"][index], '%Y-%m-%dT%H:%M:%S.%f')
                            this_sleep_time = datetime.strptime(json_entry.get("startTime", None),
                                                                '%Y-%m-%dT%H:%M:%S.%f')
                            delta_minutes = (this_sleep_time - last_wake_time).seconds // 60
                            self.data["minutesAwake"][index] += delta_minutes
                            # Update endTime to the current endTime
                            self.data["endTime"][index] = json_entry.get("endTime", None)

                            # Increment the summary levels
                            for key in self.levels_summary_keys:
                                summary = json_entry['levels']['summary']
                                if key in summary:
                                    self.data[f"summary_{key}_mins"][index] += json_entry['levels']['summary'][key]['minutes']

                    elif json_date > current_date:
                        # The current date has no sleep, skip and move to the next date
                        log("No sleep data for", current_date)
                        current_date += timedelta(days=1)

                    last_json_date = json_date_str

                # TODO: Handle missing data and errors

        return self.data


# TODO: Implement proper logging
def log(*args):
    print(*args)
    pass
