# Example using fitout to extract basic sleep info and write out some data to a CSV file.
#
# Install fitout with:
#   pip install fitout
#
# Run this script with:
#   python sleep_to_csv.py


from datetime import date, datetime
import fitout as fo

def jsontime_to_xls_time(time_str):
    # Return a data time in the format dd/mm/yyyy hh:mm
    this_sleep_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f')

    return  f"{this_sleep_time.day:02d}/{this_sleep_time.month:02d}/{this_sleep_time.year} {this_sleep_time.hour:02d}:{this_sleep_time.minute:02d}"

def mins_awake_to_xls_time(mins_awake):
    # Return the minutes awake in the format hh:mm
    return f"{mins_awake // 60}:{mins_awake % 60:02d}"

def main():
    # Specify the location where the Takeout zip files was extracted
    takeout_dir = 'C:/Dev/Fitbit/Google/'
    # Use the NativeFileLoader to load the data from the extracted files
    data_source = fo.NativeFileLoader(takeout_dir)

    # Specify the desired date range.
    start_date = date(2023, 1, 1)
    end_date = date(2024, 1, 1)
    bsi_importer = fo.BasicSleepInfo(data_source)
    bsi_data = bsi_importer.get_data(start_date, end_date)

    # # Export basic sleep data: Sleep, Wake, Minutes Awake to CSV file
    output_file = f"user_data/basic_sleep_{start_date.year}.csv"
    with open(output_file, 'w') as f:
        f.write("Sleep,Wake,Awake\n")
        for i in range(len(bsi_data['dateOfSleep'])-1):
            if bsi_data['startTime'][i] is not None:
                f.write(f"{jsontime_to_xls_time(bsi_data['startTime'][i])},{jsontime_to_xls_time(bsi_data['endTime'][i])},{mins_awake_to_xls_time(bsi_data['minutesAwake'][i])}\n")
            else:
                f.write(",,\n")

if __name__ == "__main__":
    main()
