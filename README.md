# pyFitOut
[![GitHub license](https://img.shields.io/github/license/kev-m/pyFitOut)](https://github.com/kev-m/pyFitOut/blob/development/LICENSE.txt)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fitout?logo=pypi)](https://pypi.org/project/fitout/)
[![semver](https://img.shields.io/badge/semver-2.0.0-blue)](https://semver.org/)
[![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/kev-m/pyFitOut?sort=semver)](https://github.com/kev-m/pyFitOut/releases)
[![Code style: autopep8](https://img.shields.io/badge/code%20style-autopep8-000000.svg)](https://pypi.org/project/autopep8/)

<!-- ![pyFitOut logo](https://github.com/kev-m/pyFitOut/blob/development/docs/source/figures/Logo_small.png) -->

The **pyFitOut** project is an open source Python library for extracting FitBit data from Google Takeout.

<!-- For detailed documentation, refer to the [pyFitOut Documentation](https://pyFitOut.readthedocs.io/). -->

## Installation

Use pip to install:
```bash
pip install fitout
```

## Example

How to use pyFitOut:

### Export
Export your [FitBit data](https://www.fitbit.com/settings/data/export), using [Google Takeout](https://takeout.google.com/settings/takeout/custom/fitbit?pli=1).

**Note:** Currently only export to zip is supported, and the zip files must be extracted to your local drive.

Once the export is complete, download the zip file and extract it. I use `C:/Dev/Fitbit/Google/`. 
This directory is the `takeout_dir`.

### Trivial Example
```python
import fitout as fo
from datetime import date

def main():
    # Specify the location where the Takeout zip files was extracted
    takeout_dir = 'C:/Dev/Fitbit/Google/'
    # Use the NativeFileLoader to load the data from the extracted files
    data_source = fo.NativeFileLoader(takeout_dir)
    
    # Specify the desired date range.
    start_date = date(2024, 10, 1)
    end_date = date(2024, 10, 31)
    
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

### Plotting Example with Numpy and Matplotlib
**Note:** To run this example, you will need to install the dependencies:
```bash
pip install matplotlib numpy
```

```python
from datetime import date
import numpy as np
import matplotlib.pyplot as plt
import fitout as fo

def main():
    # Specify the location where the Takeout zip files was extracted
    takeout_dir = 'C:/Dev/Fitbit/Google/'
    # Use the NativeFileLoader to load the data from the extracted files
    data_source = fo.NativeFileLoader(takeout_dir)

    # Specify the desired date range.
    start_date = date(2024, 10, 1)
    end_date = date(2024, 10, 31)

    # Generate a list of dates for the date range, for informational or plotting purposes.
    dates = fo.dates_array(start_date, end_date)

    # Create the breathing rate importer and fetch the data.
    breather_importer = fo.BreathingRate(data_source, 1)
    breathing_data = breather_importer.get_data(start_date, end_date)

    # Create the heart rate variability importer and fetch the data.
    hrv_importer = fo.HeartRateVariability(data_source)
    hrv_data = hrv_importer.get_data(start_date, end_date)

    # Create the resting heart rate importer and fetch the data.
    rhr_importer = fo.RestingHeartRate(data_source)
    rhr_data = rhr_importer.get_data(start_date, end_date)

    # Fill in missing values with the mean of the neighbouring values
    breathing_data = fo.fill_missing_with_neighbours(breathing_data)
    hrv_data = fo.fill_missing_with_neighbours(hrv_data)
    rhr_data = fo.fill_missing_with_neighbours(rhr_data)

    # Adjust buggy data (typically values that are too high or too low) to the mean of the neighbouring values
    # These values depend on your personal ranges.
    breathing_data = fo.fix_invalid_data_points(breathing_data, 10, 20)
    hrv_data = fo.fix_invalid_data_points(hrv_data, 20, 50)
    rhr_data = fo.fix_invalid_data_points(rhr_data, 46, 54)

    # Convert lists to numpy arrays
    dates_array = np.asarray(dates)
    breathing_data_array = np.array(breathing_data).astype(float)
    hrv_data_array = np.array(hrv_data).astype(float)
    rhr_data_array = np.array(rhr_data).astype(float)


    # Create a combined calmness index as follows: 100-(RHR/2 + breathing rate*2 - HRV)
    calmness_index = 100 - (rhr_data_array / 2. + breathing_data_array * 2. - hrv_data_array)

    # Plot the calmness index
    plt.figure(figsize=(10, 6))
    plt.plot(dates_array, calmness_index, marker='o', linestyle='-', color='b')
    plt.xlabel('Date')
    plt.ylabel('Calmness Index')
    plt.title('Calmness Index Over Time')
    plt.ylim(60, 95)  # Set the y-range
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()  
    # Fit a 4th order polynomial to the calmness index data
    dates_axis = np.arange(len(dates_array))
    polynomial_coefficients = np.polyfit(dates_axis, calmness_index, 4)
    polynomial = np.poly1d(polynomial_coefficients)
    fitted_calmness_index = polynomial(dates_axis)

    # Plot the fitted polynomial
    plt.plot(dates_array, fitted_calmness_index, linestyle='--', color='r', label='4th Order Polynomial Fit')
    plt.legend()

    plt.show()

    plt.show()
if __name__ == "__main__":
    main()
```

### More Examples

For more examples, see the [examples](https://github.com/kev-m/pyFitOut/tree/development/examples) directory.

## Contributing

If you'd like to contribute to **pyFitOut**, follow the guidelines outlined in the [Contributing Guide](https://github.com/kev-m/pyFitOut/blob/development/CONTRIBUTING.md).

## License

See [`LICENSE.txt`](https://github.com/kev-m/pyFitOut/blob/development/LICENSE.txt) for more information.

## Contact

For inquiries and discussion, use [pyFitOut Discussions](https://github.com/kev-m/pyFitOut/discussions).

## Issues

For issues related to this Python implementation, visit the [Issues](https://github.com/kev-m/pyFitOut/issues) page.

