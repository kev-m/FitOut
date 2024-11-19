"""Implementations of Sleep information Importers."""

from datetime import timedelta, time, datetime
import json

from importers.base import BaseImporter
from fitout.helpers import days_ago, todays_date


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
