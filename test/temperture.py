import pandas as pd
from datetime import datetime
import time
from jtop import jtop
import os

# Set the path to your CSV file
csv_file_path = 'public/logs/temperture/log_temperture.csv'

# Create an empty DataFrame with the desired column names
columns = ['Time', 'Uptime', 'CPU1', 'CPU2', 'CPU3', 'CPU4', 'CPU5', 'CPU6', 'RAM', 'SWAP', 'EMC', 'GPU',
           'APE', 'NVDEC', 'NVENC', 'NVJPG', 'NVJPG1', 'SE', 'VIC', 'Fan pwmfan0', 'Temp CPU', 'Temp CV0',
           'Temp CV1', 'Temp CV2', 'Temp GPU', 'Temp SOC0', 'Temp SOC1', 'Temp SOC2', 'Temp tj', 'Power tj',
           'Power TOT', 'jetson_clocks', 'nvp model']

df = pd.DataFrame(columns=columns)

if not os.path.exists(csv_file_path):
    # If the file doesn't exist, create it with headers
    df.to_csv(csv_file_path, header=True)

with jtop() as jetson:
    while jetson.ok():
        # Read tegra stats
        stats = jetson.stats

        # Convert time and uptime to string for DataFrame
        stats['Time'] = stats['time'].strftime('%Y-%m-%d %H:%M:%S')
        stats['Uptime'] = str(stats['uptime'])

        # Append data to the DataFrame
        df = pd.concat([df, pd.DataFrame([stats])])

        # Save the DataFrame to CSV
        if os.path.exists(csv_file_path) and os.path.getsize(csv_file_path) > 0:
            header_exists = False
        else:
            header_exists = True

        df.to_csv(csv_file_path, mode='a', header=header_exists)

        # Clear the DataFrame for the next 5-minute interval
        df = pd.DataFrame(columns=columns)

        # Wait for 15 seconds before the next iteration
        time.sleep(60)
