# pyFitOut
[![GitHub license](https://img.shields.io/github/license/kev-m/pyFitOut)](https://github.com/kev-m/pyFitOut/blob/main/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyFitOut?logo=pypi)](https://pypi.org/project/pyFitOut/)
[![semver](https://img.shields.io/badge/semver-2.0.0-blue)](https://semver.org/)
[![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/kev-m/pyFitOut?sort=semver)](https://github.com/kev-m/pyFitOut/releases)
[![Code style: autopep8](https://img.shields.io/badge/code%20style-autopep8-000000.svg)](https://pypi.org/project/autopep8/)

<!-- ![pyFitOut logo](https://github.com/kev-m/pyFitOut/blob/master/docs/source/figures/Logo_small.png) -->

The **pyFitOut** project is an open source library for extracting FitBit health data from Google Takout.

<!-- For detailed documentation, refer to the [pyFitOut Documentation](https://pyFitOut.readthedocs.io/). -->

## Installation

Use pip to install:
```bash
pip install fitout
```

## Example

```python
import fitout as fo
from datetime import date

def main():
    takeout_dir = "C:\Dev\Fitbit\Google\Takeout"

    start_date = date(2024, 10, 1)
    end_date = date(2024, 11, 5)

    dates = fo.dates_array(start_date, end_date)
    print("Dates:", dates)

    breather_importer = fo.BreathingRate(takeout_dir, 1)
    breathing_data = breather_importer.get_data(start_date, end_date)
    print("Breathing rate:", breathing_data)

    hrv_importer = fo.HeartRateVariability(takeout_dir)
    hrv_data = hrv_importer.get_data(start_date, end_date)
    print("HRV:", hrv_data)

    rhr_importer = fo.RestingHeartRate(takeout_dir)
    rhr_data = rhr_importer.get_data(start_date, end_date)
    print("RHR:", rhr_data)


if __name__ == "__main__":
    main()
```

## Contributing

If you'd like to contribute to **pyFitOut**, follow the guidelines outlined in the [Contributing Guide](https://github.com/kev-m/pyFitOut/blob/master/CONTRIBUTING.md).

## License

See [`LICENSE.txt`](https://github.com/kev-m/pyFitOut/blob/master/LICENSE.txt) for more information.

## Contact

For inquiries and discussion, use [pyFitOut Discussions](https://github.com/kev-m/pyFitOut/discussions).

## Issues

For issues related to this Python implementation, visit the [Issues](https://github.com/kev-m/pyFitOut/issues) page.

