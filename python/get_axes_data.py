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
b_top = [0] * x_len
b_bottom = [0] * x_len
b_diff = [0] * x_len
ax.set_ylim(y_range)

# Create blank lines to update live
line_top,  = ax.plot(xs, b_top, label="ALS31313KLEATR-2000 Front")
line_bottom, = ax.plot(xs, b_bottom, label="ALS31313KLEATR-2000 Rear" )
line_diff, = ax.plot(xs, b_diff, label="Front - Rear")

# Plot labels
plt.title("Magnetic Field Strength over Time")
plt.xlabel("Samples")
plt.ylabel("B-Field Strength [G]")
plt.legend()

def raw2int(vals):
    hex_str = ""
    for val in vals:
        hex_val = hex(val)[2:]
        if (len(hex_val) == 1):
            hex_val = "0" + hex_val
        hex_str += hex_val

    # print(f"Hex str: {hex_str}")
    signed_int = twos_complement(hex_str, 32)
    return signed_int

def compute_Bt(x, y, z):
    return round(math.sqrt(x ** 2 + y ** 2 + z ** 2), 2)

def twos_complement(hexstr, bits):
    value = int(hexstr, 16)
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value

# get available serial ports
def get_ports():
    return serial.tools.list_ports.comports()

def animate(i, b_top, b_bottom, b_diff):
    # get B-field reading from each sensor
    sensor_data = get_data_point()
    (_, _, _, _, sensor_top, _, _, _, sensor_bottom, sensor_diff) = sensor_data

    b_top.append(sensor_top)
    b_bottom.append(sensor_bottom)
    b_diff.append(sensor_diff)

    b_top  = b_top[-x_len:]
    b_bottom = b_bottom[-x_len:]
    b_diff = b_diff[-x_len:]

    line_top.set_ydata(b_top)
    line_bottom.set_ydata(b_bottom)
    line_diff.set_ydata(b_diff)

    return (line_top, line_bottom, line_diff)

def get_data_point():
    n = 24
    data = s.read(n) # read stream of n bytes
    # print(f"Raw data: {data}")
    data_list = list(data)
    # print(f"Data list: {data_list}")
    timestamp = dt.datetime.now().strftime('%H:%M:%S.%f')

    # extract data components
    # top ALS31313KLEATR-2000 
    x1 = data_list[0:4]
    y1 = data_list[4:8]
    z1 = data_list[8:12]

    # bottom ALS31313KLEATR-2000 
    x2 = data_list[12:16]
    y2 = data_list[16:20]
    z2 = data_list[20:24]

    # convert data from hex to floats
    x1 = raw2int(x1)
    y1 = raw2int(y1)
    z1 = raw2int(z1)
    b1 = (x1, y1, z1)

    x2 = raw2int(x2)
    y2 = raw2int(y2)
    z2 = raw2int(z2)
    b2 = (x2, y2, z2)

    Bt1 = compute_Bt(x1, y1, z1)
    Bt2 = compute_Bt(x2, y2, z2)
    Bt_diff = Bt1 - Bt2
    b_fields = (timestamp, x1, y1, z1, Bt1, x2, y2, z2, Bt2, Bt_diff)
    print(f"Top: {b1}")
    print(f"Bottom: {b2}")
    print(f"Difference: {Bt_diff}")

    return b_fields # in the form (timestamp, ALS31313KLEATR-500 reading, ALS31313KLEATR-1000 reading, ALS31313KLEATR-2000)

ports = get_ports()
baud_rate = 115200
timeout = 5 # seconds

# define and open port
s = serial.Serial(ports[0].device, baud_rate, timeout=timeout) # default transaction size is 1 byte
if (not(s.is_open)):
    s.open()

def main():
    while True:
        # uncomment the two lines below for live plotting of hall-effect sensor readings
        # additionally, comment out the csv generation lines
        # anim = animation.FuncAnimation(fig, animate, fargs=(b_top, b_bottom, b_diff), interval=50, blit=True, cache_frame_data=False)
        # plt.show()

        # uncomment to save data as csv
        # data will run until user performs Ctrl+c
        path = '/home/pkuhle/src/wheel-adhesion/wheel_adhesion_data/WAD_PCB_data/' # path on local machine
        path = '/data/wad/csv_files/' # path to .csv files on SBC
        filename = dt.datetime.now().strftime(path + 'magnetic_data_%m-%d-%Y_%H-%M-%S.csv')
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            header = ['Timestamp', 'x-top', 'y-top', 'z-top', 'Bt-top', 'x-bottom', 'y-bottom', 'z-bottom', 'Bt-bottom', 'Bt-difference']
            writer.writerow(header)
            while True:
                data = list(get_data_point())
                writer.writerow(data)

if __name__ == "__main__":
    main()