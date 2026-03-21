import pytest
from datetime import date
from fitout.importers.exercise import ExerciseInfo

class MockDataSource:
    def __init__(self, data):
        self.data_path = 'Takeout/Fitbit/Global Export Data/'
        self.data = data
        self.dir_path = '/'
        self.zip_files = [f"{self.data_path}exercise-0.json"]

    def open(self, filename):
        import io
        import json
        return io.StringIO(json.dumps(self.data))


def test_exercise_info_get_raw_sessions():
    mock_data = [
        {
            "logId": 12345,
            "activityName": "Walk",
            "startTime": "03/03/22 12:41:37"
        },
        {
            "logId": 12346,
            "activityName": "Run",
            "startTime": "03/04/22 08:00:00"
        },
        {
            "logId": 12347,
            "activityName": "Bike",
            "startTime": "03/10/22 14:00:00"
        }
    ]
    
    data_source = MockDataSource(mock_data)
    importer = ExerciseInfo(data_source)
    
    # Test valid date range covering first two
    start_d = date(2022, 3, 1)
    end_d = date(2022, 3, 5)
    
    sessions = importer.get_raw_sessions(start_d, end_d)
    
    assert len(sessions) == 2
    assert sessions[0]["activityName"] == "Walk"
    assert sessions[1]["activityName"] == "Run"
    
    # Test out of range
    start_d2 = date(2022, 4, 1)
    end_d2 = date(2022, 4, 10)
    sessions2 = importer.get_raw_sessions(start_d2, end_d2)
    assert len(sessions2) == 0

    # Test exact bounds
    start_d3 = date(2022, 3, 10)
    end_d3 = date(2022, 3, 10)
    sessions3 = importer.get_raw_sessions(start_d3, end_d3)
    assert len(sessions3) == 1
    assert sessions3[0]["activityName"] == "Bike"

def test_exercise_info_get_data_raises():
    mock_data = []
    data_source = MockDataSource(mock_data)
    importer = ExerciseInfo(data_source)
    
    with pytest.raises(NotImplementedError):
        importer.get_data()
