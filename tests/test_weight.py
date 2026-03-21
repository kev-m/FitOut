import pytest
from datetime import date
from fitout.importers.weight import WeightInfo

class MockDataSource:
    def __init__(self, data):
        self.data_path = 'Takeout/Fitbit/Global Export Data/'
        self.data = data
        self.dir_path = '/'
        self.zip_files = [f"{self.data_path}weight-2022-03-02.json"]

    def open(self, filename):
        import io
        import json
        return io.StringIO(json.dumps(self.data))


def test_weight_info_get_raw_sessions():
    mock_data = [
        {
            "logId": 1686441599000,
            "weight": 130.2,
            "bmi": 17.59,
            "date": "06/10/23",
            "time": "23:59:59",
            "source": "API"
        },
        {
            "logId": 1686959999000,
            "weight": 130.5,
            "bmi": 17.62,
            "fat": 20.0,
            "date": "06/16/23",
            "time": "12:30:00",
            "source": "API"
        }
    ]
    
    data_source = MockDataSource(mock_data)
    importer = WeightInfo(data_source)
    
    # Test valid date range covering first record only
    start_d = date(2023, 6, 1)
    end_d = date(2023, 6, 12)
    
    sessions = importer.get_raw_sessions(start_d, end_d)
    
    assert len(sessions) == 1
    assert sessions[0]["weight"] == 130.2
    assert sessions[0]["bmi"] == 17.59
    assert "fat" not in sessions[0]
    
    # Test valid date range covering both
    start_d2 = date(2023, 6, 1)
    end_d2 = date(2023, 6, 20)
    sessions2 = importer.get_raw_sessions(start_d2, end_d2)
    assert len(sessions2) == 2
    assert sessions2[1]["weight"] == 130.5
    assert sessions2[1]["fat"] == 20.0

def test_weight_info_get_data_raises():
    mock_data = []
    data_source = MockDataSource(mock_data)
    importer = WeightInfo(data_source)
    
    with pytest.raises(NotImplementedError):
        importer.get_data()
