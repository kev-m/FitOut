"""Implementations of Heart Rate Importers."""

from datetime import timedelta, datetime
import json

from importers.base import BaseImporter, BasicCSVImporter, TwoLineCSVImporter
from fitout.helpers import hours_ago, days_ago, todays_date, number_precision


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


# Importer for basic heart rate data
class BasicHeartRate(BasicCSVImporter):
    """
    Importer for basic heart rate data.

    The basic heart rate importer performs basic processing of the raw heart rate data by converting the semi-random
    entries into a list of values at a regular interval. The default reporting interval is every 10 seconds, but this
    can be changed using the set_sampling_interval method.
    """

    def __init__(self, data_source, precision=0):
        """
        Constructs the heart rate reporter.

        Args:
            data_source (BaseFileLoader): The data source used to load data.
            precision (int): The precision for numerical data (default is 0).
        """
        # C:\Dev\Fitbit\Google\Takeout\Fitbit\Physical Activity_GoogleData\heart_rate_2024-10-27.csv
        # timestamp,beats per minute
        # 2024-10-27T00:00:04Z,65.0
        # 2024-10-27T00:00:09Z,62.0
        # 2024-10-27T00:00:14Z,61.0
        # 2024-10-27T00:00:19Z,62.0
        # 2024-10-27T00:00:34Z,63.0
        # 2024-10-27T00:00:39Z,62.0
        # 2024-10-27T00:00:44Z,65.0
        # ...
        #
        super().__init__(data_source, 'Takeout/Fitbit/Physical Activity_GoogleData/', precision)
        self.data_file = 'heart_rate_'
        self.interval_s = 10

    def set_sampling_interval(self, interval_s):
        """
        Sets the heart rate reporting interval in seconds.

        Args:
            interval_s (int): The heart rate reporting interval, in seconds.
        """
        self.interval_s = interval_s

    def get_data(self, start_time=hours_ago(10), end_time=hours_ago(1)):
        """
        Retrieves data for a range of times from start_date to end_date.

        Args:
            start_time (datetime.datetime, optional): The start time for data retrieval. Defaults to 10 days ago.
            end_time (datetime.datetime, optional): The end time for data retrieval. Defaults to today's date.
        Returns:
            list (int): The regularised heart rate in the specified range.
        """
        num_samples = int((end_time - start_time).seconds/self.interval_s) + 1
        self.data = [None] * num_samples
        self.dates = [None] * num_samples
        current_time = start_time
        index = 0

        while index < num_samples:
            # start_date = current_date.date().strftime('%Y-%m-%d')
            # 1. Get the CSV file name from the start date
            start_date = current_time.date().strftime('%Y-%m-%d')
            csv_filename = self.data_path + self.data_file + start_date + '.csv'
            # 2. Open the CSV file using the read_csv method
            cols, data = self.read_csv(csv_filename)
            # 3. Scan through the data to find the first entry that is equal to or after the start time
            for row in data:
                # convert string to datetime
                data_time = datetime.strptime(row[0], '%Y-%m-%dT%H:%M:%SZ')
                current_rate = float(row[1])
                if data_time >= current_time:
                    # 4. For all values from that point on, calculate the heart rate by interpolation, using the sampling interval.
                    if data_time == current_time:
                        self.data[index] = number_precision(current_rate, self.precision)
                    else:
                        # interpolate between the two values
                        data_time_diff = (data_time - prev_data_time).seconds
                        sample_time_diff = (current_time - prev_data_time).seconds

                        heart_rate_diff = current_rate - prev_data_rate
                        m = heart_rate_diff/data_time_diff

                        value = prev_data_rate + m*sample_time_diff

                        self.data[index] = number_precision(value, self.precision)

                    self.dates[index] = current_time
                    index += 1
                    current_time += timedelta(seconds=self.interval_s)
                prev_data_time = data_time
                prev_data_rate = current_rate
                if index == num_samples:
                    break
            # 5. If the end time is reached before the required number of samples are found, return the data found so far
            if current_time > end_time:
                break
            # 6. If the end of the file is reached before the end time, open the next file and continue the search
            # 7. If there are no more files, return the data found so far

        return self.data
