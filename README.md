# pyFitOut
[![GitHub license](https://img.shields.io/github/license/kev-m/pyFitOut)](https://github.com/kev-m/pyFitOut/blob/development/LICENSE.txt)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fitout?logo=pypi)](https://pypi.org/project/fitout/)
[![semver](https://img.shields.io/badge/semver-2.0.0-blue)](https://semver.org/)
[![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/kev-m/pyFitOut?sort=semver)](https://github.com/kev-m/pyFitOut/releases)
[![Code style: autopep8](https://img.shields.io/badge/code%20style-autopep8-000000.svg)](https://pypi.org/project/autopep8/)

<!-- ![pyFitOut logo](https://github.com/kev-m/pyFitOut/blob/development/docs/source/figures/Logo_small.png) -->

The **pyFitOut** project is an open source Python library for extracting FitBit health data from Google Takeout.

<!-- For detailed documentation, refer to the [pyFitOut Documentation](https://pyFitOut.readthedocs.io/). -->

## Installation

Use pip to install:
```bash
pip install fitout
# or
pip install -i https://test.pypi.org/simple/ fitout
```

## Example

How to use pyFitOut:

### Export
Export your [FitBit data](https://www.fitbit.com/settings/data/export), using [Google Takeout](https://takeout.google.com/settings/takeout/custom/fitbit?pli=1).

**Note:** Currently only export to zip is supported.

Once the export is complete, download the zip file and extract it. I use `C:\Dev\Fitbit\Google\Takeout`. 
This directory is the `takeout_dir`.

```python
import fitout as fo
from datetime import date

def main():
    # Specify the location where the Takeout zip files was extracted
    takeout_dir = "C:\Dev\Fitbit\Google\Takeout"
    # Use the NativeFileLoader to load the data from the extracted files
    data_source = fo.NativeFileLoader(takeout_dir)

    # Specify the desired date range.
    start_date = date(2024, 10, 1)
    end_date = date(2024, 11, 5)

    # Generate a list of dates for the date range, for informational or plotting purposes.
    dates = fo.dates_array(start_date, end_date)
    print("Dates:", dates)

    # Create the breathing rate importer and fetch the data.
    breather_importer = fo.BreathingRate(data_source, 1)
    breathing_data = breather_importer.get_data(start_date, end_date)
    print("Breathing rate:", breathing_data)

    # Create the heart rate variability importer and fetch the data.
    hrv_importer = fo.HeartRateVariability(data_source)
    hrv_data = hrv_importer.get_data(start_date, end_date)
    print("HRV:", hrv_data)

    # Create the resting heart rate importer and fetch the data.
    rhr_importer = fo.RestingHeartRate(data_source)
    rhr_data = rhr_importer.get_data(start_date, end_date)
    print("RHR:", rhr_data)


if __name__ == "__main__":
    main()
```

## Contributing

If you'd like to contribute to **pyFitOut**, follow the guidelines outlined in the [Contributing Guide](https://github.com/kev-m/pyFitOut/blob/development/CONTRIBUTING.md).

## License

See [`LICENSE.txt`](https://github.com/kev-m/pyFitOut/blob/development/LICENSE.txt) for more information.

## Contact

For inquiries and discussion, use [pyFitOut Discussions](https://github.com/kev-m/pyFitOut/discussions).

## Issues

For issues related to this Python implementation, visit the [Issues](https://github.com/kev-m/pyFitOut/issues) page.

