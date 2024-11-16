# Example using fitout to extract basic sleep info and write out some data to a CSV file.
#
# Install fitout with:
#   pip install fitout
#
# Run this script with:
#   python sleep_to_csv.py


from datetime import date, datetime
import fitout as fo

# Main function to demonstrate the use of the Fitbit ZIP file data source
def main():
    # Specify the location where the Takeout zip file is
    takeout_zip = 'C:/Dev/Fitbit/Google/takeout-20241107T140017Z-001.zip'
    # Use the ZipFileLoader to load the data from the extracted files
    data_source = fo.ZipFileLoader(takeout_zip)

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
