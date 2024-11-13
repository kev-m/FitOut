# Example using fitout with and plotting with Numpy and Matplotlib.
#
# Install fitout with:
#   pip install fitout
#
# Install dependencies with:
#   pip install numpy matplotlib
#
# Run this script with:
#   python numpy_plotting.py

import numpy as np
import matplotlib.pyplot as plt
from datetime import date
import fitout as fo

def main():
    # Specify the location where the Takeout zip files was extracted
    takeout_dir = "C:\Dev\Fitbit\Google\Takeout"
    # Use the NativeFileLoader to load the data from the extracted files
    data_source = fo.NativeFileLoader(takeout_dir)

    # Specify the desired date range.
    start_date = date(2023, 1, 1)
    end_date = date(2023, 12, 31)
    # start_date = date(2024, 7, 1)
    # end_date = date(2024, 7, 31)

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

    # Export dates, calmness index to CSV file
    write_csv = False
    if write_csv:
        output_file = f"user_data/calmness_index_{start_date.year}.csv"
        with open(output_file, 'w') as f:
            f.write("Date,Calmness Index\n")
            for i in range(len(dates_array)):
                f.write(f"{dates_array[i]},{fo.number_precision(calmness_index[i], 0)}\n")


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

if __name__ == "__main__":
    main()
