"""Implementations of Weight information Importers."""

import json
from datetime import datetime

from fitout.importers.base import BaseImporter
from fitout.helpers import days_ago, todays_date


class WeightInfo(BaseImporter):
    """
    Importer for weight and BMI data.
    """

    def __init__(self, data_source, precision=1):
        """
        Constructs the weight information importer instance.

        Args:
            data_source (BaseFileLoader): The data source used to load data.
            precision (int): The precision for numerical data (default is 1).
        """
        super().__init__(data_source, 'Takeout/Fitbit/Global Export Data/', precision)
        self.data_prefix = 'weight-'

    def get_data(self, start_date=days_ago(10), end_date=todays_date()):
        """
        Not implemented for WeightInfo. Use get_raw_sessions instead, 
        as weigh-ins are discrete events rather than daily continuous arrays.
        """
        raise NotImplementedError("Use get_raw_sessions to retrieve individual weight records.")

    def get_raw_sessions(self, start_date=days_ago(10), end_date=todays_date()):
        """
        Retrieves all raw weight events for a range of dates from start_date to end_date.

        Args:
            start_date (datetime.date, optional): The start date for data retrieval.
            end_date (datetime.date, optional): The end date for data retrieval.
            
        Returns:
            list[dict]: A list of dictionaries, where each dictionary represents a distinct weigh-in.
        """
        target_files = []
        if hasattr(self.data_source, 'dir_path'):
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
                        date_str = item.get('date')
                        time_str = item.get('time')
                        if not date_str or not time_str:
                            continue
                            
                        # Fitbit format: MM/DD/YY HH:MM:SS
                        try:
                            # 06/10/23 23:59:59
                            dt_str = f"{date_str} {time_str}"
                            dt = datetime.strptime(dt_str, '%m/%d/%y %H:%M:%S')
                        except ValueError:
                            continue
                                
                        item_date = dt.date()
                        
                        if start_date <= item_date <= end_date:
                            # Standardise time format
                            item['startTimeIso'] = dt.isoformat()
                            item['weight'] = round(float(item['weight']), self.precision) if 'weight' in item else None
                            if 'bmi' in item:
                                item['bmi'] = round(float(item['bmi']), 2)
                            if 'fat' in item:
                                item['fat'] = round(float(item['fat']), 1)
                            
                            raw_sessions.append(item)
            except (FileNotFoundError, KeyError):
                continue
                
        # Sort chronologically
        raw_sessions.sort(key=lambda x: x.get('startTimeIso', ''))
        return raw_sessions
