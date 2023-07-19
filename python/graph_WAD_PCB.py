import os
import pandas as pd
import matplotlib.pyplot as plt

dir = "/home/pkuhle/src/wheel-adhesion/wheel_adhesion_data/WAD_PCB_data/"
files = os.listdir(dir + 'raw')
for file in files:
    data = pd.read_csv(os.path.join(dir, file))

    # Extract sensor readings from csv
    sensor_500  = data.loc[:, "500 G Sensor"] # data from ALS31313KLEATR-500
    sensor_1000 = data.loc[:, "1000 G Sensor"] # data from ALS31313KLEATR-500
    sensor_2000 = data.loc[:, "2000 G Sensor"] # data from ALS31313KLEATR-500 
    times = data.loc[:, "Timestamp"] # timestamps

    seconds = [] # list of all times in seconds for current file
    for time in times:
        time_list = time.split(":")
        hour = float(time_list[0])
        minute = float(time_list[1])
        second = float(time_list[2])
        total_seconds = 3600*hour + 60*minute + second
        seconds.append(total_seconds)

    # calculate time elapsed vector
    t = [0]
    for i in range(1, len(seconds)):
        delta_t = seconds[i] - seconds[i-1]
        t.append(t[i-1] + delta_t)

    # Plotting
    plt.plot(t, sensor_500, label='500 G Sensor')
    plt.plot(t, sensor_1000, label='1000 G Sensor')
    plt.plot(t, sensor_2000, label='2000 G Sensor')
    plt.legend()
    plt.title("Total Magnetic Field vs Time for WAD PCB Sensors")
    plt.xlabel('Time (s)')
    plt.ylabel('Magnetic Field Strength (G)')
    plt.savefig(dir + 'plots')