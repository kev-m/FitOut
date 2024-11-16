# Example using fitout with no depdenencies on any other packages.
# Install fitout with:
#   pip install fitout
# Run this script with:
#   python native.py

from datetime import date
import fitout as fo

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
