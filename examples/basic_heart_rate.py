# Example using fitout with no depdenencies on any other packages.
# Install fitout with:
#   pip install fitout
# Run this script with:
#   python basic_heart_rate.py

from datetime import datetime
import fitout as fo

def main():
    # Specify the location where the Takeout zip file is
    takeout_dir = 'C:/Dev/Fitbit/Google/'
    # Use the NativeFileLoader to load the data from the extracted files
    data_source = fo.NativeFileLoader(takeout_dir)

    # Specify the desired time range.
    start_time = datetime(2024, 10, 1, 10, 0)
    end_time = datetime(2024, 10, 1, 10, 1)

    # Extract the heart rate data for the specified date and time range.
    basic_heart_rate = fo.BasicHeartRate(data_source)
    heart_rate_data = basic_heart_rate.get_data(start_time, end_time)
    print("Heart rate data (10s):", heart_rate_data)

    # Change the sampling interval to 5 seconds.
    basic_heart_rate.set_sampling_interval(5)
    heart_rate_data = basic_heart_rate.get_data(start_time, end_time)
    print("Heart rate data (5s):", heart_rate_data)


if __name__ == "__main__":
    main()
