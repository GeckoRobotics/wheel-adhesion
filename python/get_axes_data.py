import serial
import serial.tools.list_ports
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import csv

#### CODE FOR LIVE PLOTTING TOTAL B-FIELD ####

# Create figure for plotting
x_len = 200
y_range = [0, 400]
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

# Plot animation function
def animate(i, b_500, b_1000, b_2000):
    # get B-field reading from each sensor
    sensor_data = get_data_point()
    (_, _, _, _, sensor_500, _, _, _, sensor_1000, _, _, _, sensor_2000) = sensor_data

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


#### CODE FOR COMPUTING B-FIELDS FROM DATA FROM SERIAL PORT ####

# converts raw data to signed int
# takes in list of 8 bit unsigned ints
def raw2int(vals):
    hex_str = ""
    for val in vals:
        hex_val = hex(val)[2:] # convert in to hex string
        if (len(hex_val) == 1):
            # prepend zero if hex_val can be represented with only one hex character
            # prevents loss of four bits when appending to hex_str
            hex_val = "0" + hex_val 
        hex_str += hex_val

    signed_int = twos_complement(hex_str, 32)
    return signed_int

# Compute magnitude of sensor reading
def compute_Bt(x, y, z):
    return round(math.sqrt(x ** 2 + y ** 2 + z ** 2), 2)

# gets signed int from unsigned int by computing 2s complement
def twos_complement(hexstr, bits):
    value = int(hexstr, 16) # unsigned int
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value

# get available serial ports
def get_ports():
    return serial.tools.list_ports.comports()

# get one sensor reading from serial port
def get_data_point():
    n = 36
    data = s.read(n) # read stream of n bytes (byte object)
    data_list = list(data) # creats list of values by converting every 8 bytes into an unsigned int
    timestamp = dt.datetime.now().strftime('%H:%M:%S.%f')

    # extract raw data components (4 bytes each)
    # data from ALS31313KLEATR-500
    x1 = data_list[0:4]
    y1 = data_list[4:8]
    z1 = data_list[8:12]

    # data from ALS31313KLEATR-1000
    x2 = data_list[12:16]
    y2 = data_list[16:20]
    z2 = data_list[20:24]

    # data from ALS31313KLEATR-2000
    x3 = data_list[24:28]
    y3 = data_list[28:32]
    z3 = data_list[32:]

    # convert data from hex to signed ints
    # divide by sensitivity of sensor to convert measurement to Gauss
    sens_500 = 4 # [LSB/G], sensitivity of ALS31313KLEATR-500
    x1 = raw2int(x1) / 4
    y1 = raw2int(y1) / 4
    z1 = raw2int(z1) / 4
    b1 = (x1, y1, z1)

    sens_1000 = 2 # [LSB/G], sensitivity of ALS31313KLEATR-1000
    x2 = raw2int(x2) / 2
    y2 = raw2int(y2) / 2 
    z2 = raw2int(z2) / 2
    b2 = (x2, y2, z2)

    # sensitivity for ALS31313KLEATR-2000 is 1 LSB/G
    x3 = raw2int(x3)
    y3 = raw2int(y3)
    z3 = raw2int(z3)
    b3 = (x3, y3, z3)

    # Magnitude of B-field reading for ALS31313KLEATR-500, 1000, and 2000, respectively
    Bt1 = compute_Bt(x1, y1, z1)
    Bt2 = compute_Bt(x2, y2, z2)
    Bt3 = compute_Bt(x3, y3, z3)

    print(f"500: {b1}")
    print(f"1000: {b2}")
    print(f"2000: {b3}\n")

    b_fields = (timestamp, x1, y1, z1, Bt1, x2, y2, z2, Bt2, x3, y3, z3, Bt3)
    return b_fields




ports = get_ports()
baud_rate = 115200
timeout = 10 # seconds

# define and open port
s = serial.Serial(ports[0].device, baud_rate, timeout=timeout) # default transaction size is 1 byte
if (not(s.is_open)):
    s.open()

def main():
    while True:
        # uncomment lines 157-158 for live plotting of total B-field for each of the three sensors
        # anim = animation.FuncAnimation(fig, animate, fargs=(b_500, b_1000, b_2000), interval=50, blit=True, cache_frame_data=False)
        # plt.show()

        # uncomment lines 162-171 to save data as csv
        # data collection will continue until user performs Ctrl+c
        path = '/home/pkuhle/src/wheel-adhesion/wheel_adhesion_data/WAD_PCB_data/' # path on local machine (SBC)
        path = '/data/wad/csv_files/' # path to .csv files on SBC
        filename = dt.datetime.now().strftime(path + 'magnetic_data_%m-%d-%Y_%H-%M-%S.csv')
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            header = ['Timestamp', 'x-500', 'y-500', 'z-500', 'Bt-500', 'x-1000', 'y-1000', 'z-1000', 'Bt-1000', 'x-2000', 'y-2000', 'z-2000', 'Bt-2000']
            writer.writerow(header)
            while True:
                data = list(get_data_point())
                writer.writerow(data)

if __name__ == "__main__":
    main()