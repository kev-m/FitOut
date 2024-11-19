"""Implementations of Breathing Rate Imports."""

from importers.base import TwoLineCSVImporter

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
