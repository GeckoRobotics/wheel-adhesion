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
b_500 = [0] * x_len
b_1000 = [0] * x_len
b_2000 = [0] * x_len
bt = [0] * x_len
ax.set_ylim(y_range)

# Create blank lines to update live
line_500,  = ax.plot(xs, b_500, label="ALS31313KLEATR-500")
line_1000, = ax.plot(xs, b_1000, label="ALS31313KLEATR-1000" )
line_2000, = ax.plot(xs, b_2000, label="ALS31313KLEATR-2000")

# Plot labels
plt.title("Magnetic Field Strength over Time")
plt.xlabel("Samples")
plt.ylabel("B-Field Strength [G]")
plt.legend()

def raw2int(vals):
    hex_str = "".join(hex(x)[2:] for x in vals)
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

def animate(i, b_500, b_1000, b_2000):
    # get B-field reading from each sensor
    sensor_data = get_data_point()
    (_, sensor_500, sensor_1000, sensor_2000) = sensor_data

    b_500.append(sensor_500)
    b_1000.append(sensor_1000)
    b_2000.append(sensor_2000)

    b_500  = b_500[-x_len:]
    b_1000 = b_1000[-x_len:]
    b_2000 = b_2000[-x_len:]

    line_500.set_ydata(b_500)
    line_1000.set_ydata(b_1000)
    line_2000.set_ydata(b_2000)

    return (line_500, line_1000, line_2000)

def get_data_point():
    n = 36
    data = s.read(n) # read stream of n bytes
    # print(f"Raw data: {data}")
    data_list = list(data)
    timestamp = dt.datetime.now().strftime('%H:%M:%S.%f')

    # extract data components
    x1 = data_list[0:4]
    y1 = data_list[4:8]
    z1 = data_list[8:12]

    x2 = data_list[12:16]
    y2 = data_list[16:20]
    z2 = data_list[20:24]

    x3 = data_list[24:28]
    y3 = data_list[28:32]
    z3 = data_list[32:]

    # convert data from hex to floats
    x1 = raw2int(x1)
    y1 = raw2int(y1)
    z1 = raw2int(z1)
    b1 = (x1, y1, z1)

    x2 = raw2int(x2)
    y2 = raw2int(y2)
    z2 = raw2int(z2)
    b2 = (x2, y2, z2)

    x3 = raw2int(x3)
    y3 = raw2int(y3)
    z3 = raw2int(z3)
    b3 = (x3, y3, z3)

    Bt1 = compute_Bt(x1, y1, z1)
    Bt2 = compute_Bt(x2, y2, z2)
    Bt3 = compute_Bt(x3, y3, z3)
    b_fields = (timestamp, Bt1, Bt2, Bt3)
    print(f"Bt: {b_fields[1:]}")
    print(f"500: {b1}")
    print(f"1000: {b2}")
    print(f"2000: {b3}\n")

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
        # anim = animation.FuncAnimation(fig, animate, fargs=(b_500, b_1000, b_2000), interval=50, blit=True, cache_frame_data=False)
        # plt.show()

        # uncomment to save data as csv
        # data will run until user performs Ctrl+c
        # path = '/home/pkuhle/src/wheel-adhesion/wheel_adhesion_data/WAD_PCB_data/' # path on local machine
        path = '/data/wad/csv_files' # path to .csv files on SBC
        filename = dt.datetime.now().strftime(path + 'magnetic_data_%m-%d-%Y_%H:%M:%S.csv')
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', '500 G Sensor', '1000 G Sensor', '2000 G Sensor'])
            while True:
                data = list(get_data_point())
                writer.writerow(data)
if __name__ == "__main__":
    main()