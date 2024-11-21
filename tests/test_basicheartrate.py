from datetime import datetime
import pytest
from unittest.mock import MagicMock

from fitout import BasicHeartRate


@pytest.fixture
def mock_datasource_csv():
    datasource = MagicMock()
    datasource.open.return_value.__enter__.return_value = MagicMock()
    datasource.open.return_value.__enter__.return_value.__iter__.return_value = iter([
        "timestamp,beats per minute",
        "2024-10-01T05:48:29Z,89.0",
        "2024-10-01T05:48:32Z,90.0",
        "2024-10-01T05:55:07Z,91.0",
        "2024-10-01T05:55:09Z,90.0",
        "2024-10-01T05:55:12Z,90.0"
    ])
    return datasource


def test_resting_heart_rate_trivial(mock_datasource_csv):
    bhr = BasicHeartRate(mock_datasource_csv)

    # Specify the desired date range.
    start_time = datetime(2024, 10, 1, 5, 48, 30)
    end_time = datetime(2024, 10, 1, 5, 55, 10)

    heart_rate_data = bhr.get_data(start_time, end_time)

    assert heart_rate_data is not None
    assert isinstance(heart_rate_data, list)
    assert len(heart_rate_data) == 41
    assert heart_rate_data[0:4] == [89, 90, 90, 90]
