"""Implementations of Heart Rate Importers."""

from datetime import timedelta
import json

from importers.base import BaseImporter, TwoLineCSVImporter
from fitout.helpers import days_ago, todays_date, number_precision

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
                    # return self.data
                    index += 1
                    current_date += timedelta(days=1)
                if json_date is not None:
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
