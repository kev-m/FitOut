"""Implementations of Exercise information Importers."""

import json
from datetime import datetime, timedelta

from fitout.importers.base import BaseImporter
from fitout.helpers import days_ago, todays_date


class ExerciseInfo(BaseImporter):
    """
    Importer for exercise and workout data.
    """

    def __init__(self, data_source, precision=0):
        """
        Constructs the exercise information importer instance.

        Args:
            data_source (BaseFileLoader): The data source used to load data.
            precision (int): The precision for numerical data (default is 0).
        """
        super().__init__(data_source, 'Takeout/Fitbit/Global Export Data/', precision)
        self.data_prefix = 'exercise-'

    def get_data(self, start_date=days_ago(10), end_date=todays_date()):
        """
        Not implemented for ExerciseInfo. Use get_raw_sessions instead, 
        as exercises are discrete events rather than daily continuous data.
        """
        raise NotImplementedError("Use get_raw_sessions to retrieve individual workout events.")

    def get_raw_sessions(self, start_date=days_ago(10), end_date=todays_date()):
        """
        Retrieves all raw exercise events for a range of dates from start_date to end_date.

        Args:
            start_date (datetime.date, optional): The start date for data retrieval.
            end_date (datetime.date, optional): The end date for data retrieval.
            
        Returns:
            list[dict]: A list of dictionaries, where each dictionary represents a distinct exercise session.
        """
        # Fitbit takeout exercise files are typically named exercise-0.json, exercise-100.json, etc.
        # We need to scan all of them because file names do not natively indicate date ranges.
        
        target_files = []
        if hasattr(self.data_source, 'dir_path'):
            # It's native or zip
            if hasattr(self.data_source, 'zip_files'):
                target_files = [f for f in self.data_source.zip_files 
                                if f.startswith(self.data_path + self.data_prefix) and f.endswith('.json')]
            else:
                import glob
                target_files = glob.glob(self.data_source.dir_path + self.data_path + self.data_prefix + '*.json')
                # convert to relative path for the open() method of data_source
                target_files = [f.replace(self.data_source.dir_path, '').replace('\\', '/') for f in target_files]
        
        raw_sessions = []
        
        for file in target_files:
            try:
                with self.data_source.open(file) as f:
                    json_data = json.load(f)
                    for item in json_data:
                        start_time_str = item.get('startTime')
                        if not start_time_str:
                            continue
                            
                        # Fitbit format: MM/DD/YY HH:MM:SS
                        try:
                            # 03/03/22 12:41:37
                            dt = datetime.strptime(start_time_str, '%m/%d/%y %H:%M:%S')
                        except ValueError:
                            # Fallback in case of different formatting
                            try:
                                dt = datetime.fromisoformat(start_time_str.replace('Z', ''))
                            except ValueError:
                                continue
                                
                        item_date = dt.date()
                        
                        if start_date <= item_date <= end_date:
                            # To standardise time format to ISO 8601 for consumers
                            item['startTimeIso'] = dt.isoformat()
                            raw_sessions.append(item)
            except (FileNotFoundError, KeyError):
                continue
                
        # Sort chronologically
        raw_sessions.sort(key=lambda x: x.get('startTimeIso', ''))
        return raw_sessions
