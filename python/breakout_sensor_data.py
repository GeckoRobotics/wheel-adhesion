import serial
import serial.tools.list_ports
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import csv
import os
import time 

# Parameters
x_len = 200
y_range = [0, 400]


# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = list(range(0, 200))
b = [0] * x_len
ax.set_ylim(y_range)

# Create blank lines to update live
line,  = ax.plot(xs, b, label="ALS31313KLEATR-500")


# Plot labels
plt.title("Magnetic Field Strength over Time")
plt.xlabel("Samples")
plt.ylabel("B-Field Strength [G]")
plt.legend()

# get available serial ports
def get_ports():
    return serial.tools.list_ports.comports()

def animate(i, b):
    # get B-field reading from each sensor
    sensor_data = get_data_point()
    (_, sensor) = sensor_data

    b.append(sensor)

    b = b[-x_len:]
    line.set_ydata(b)

    return (line,)

def get_data_point():
    data = s.read(4) # read stream of 12 bytes
    # print(f"Raw data: {data}")
    data_list = list(data)
    timestamp = dt.datetime.now().strftime('%H:%M:%S.%f')

    # extract data components
    data = data_list[0:4]
    # convert data from hex to floats
    data = "".join(hex(x)[2:] for x in data)
    data = round(math.sqrt(int(data, 16)), 2)
    b_fields = (timestamp, data)
    # print(b_fields[1:])

    return b_fields # in the form (timestamp, ALS31313KLEATR-500 reading, ALS31313KLEATR-1000 reading, ALS31313KLEATR-2000)

ports = get_ports()
baud_rate = 115200
# define and open port
s = serial.Serial(ports[0].device, baud_rate) # default transaction size is 1 byte
if (not(s.is_open)):
    s.open()

def main():
    while True:
        # uncomment the two lines below for live plotting of hall-effect sensor readings
        # additionally, comment out the csv generation lines
        anim = animation.FuncAnimation(fig, animate, fargs=(b,), interval=50, blit=True, cache_frame_data=False)
        plt.show()

        # save data as csv
        # data will run until user performs Ctrl+c
        # path = '/home/pkuhle/src/wheel-adhesion/wheel_adhesion_data/WAD_PCB_data/'
        # filename = dt.datetime.now().strftime(path + 'magnetic_data_%m-%d-%Y_%H:%M:%S.csv')
        # with open(filename, 'w', newline='') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(['Timestamp', '500 G Sensor', '1000 G Sensor', '2000 G Sensor'])
        #     while True:
        #         data = list(get_data_point())
        #         writer.writerow(data)

if __name__ == "__main__":
    main()