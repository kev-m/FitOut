from datetime import date
import pytest
from unittest.mock import MagicMock
from fitout import RestingHeartRate


@pytest.fixture
def mock_datasource_str():
    datasource = MagicMock()
    datasource.open.return_value.__enter__.return_value = MagicMock()
    datasource.open.return_value.__enter__.return_value.read.return_value = """[{
        "value": {
            "date": "10/01/24",
            "value": 52.01231098175049
        }
        }, {
        "value": {
            "date": "10/02/24",
            "value": 53.01231098175049
        }
        }, {
        "value": {
            "date": "10/03/24",
            "value": 54.01231098175049
        }
        }, {
        "value": {
            "date": "10/04/24",
            "value": 55.069952964782715
        }
        }]"""
    return datasource

def test_resting_heart_rate_trivial(mock_datasource_str):
    rhr = RestingHeartRate(mock_datasource_str)
    rhr_data = rhr.get_data(date(2024, 10, 2), date(2024, 10, 3))

    assert rhr_data is not None
    assert isinstance(rhr_data, list)
    assert len(rhr_data) == 2
    assert rhr_data == [53, 54]

