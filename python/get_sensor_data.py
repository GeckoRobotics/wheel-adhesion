import serial
import serial.tools.list_ports
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math

# Sensor sensitivities [LSB / G]
sens_500 = 4
sens_1000 = 2
sens_2000 = 1
sensitivities = [sens_500, sens_1000, sens_2000]

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
time_axis = []
b_field = []

# get available serial ports
def get_ports():
    return serial.tools.list_ports.comports()

def animate(i, time_axis, b_field):
    time_axis.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    data_point = get_data_point()
    b_field.append(data_point)

    time_axis = time_axis[-20:]
    b_field = b_field[-20:]
    ax.clear()
    ax.plot(time_axis, b_field)

    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Magnetic Field Strength')
    plt.ylabel('Total Magnetic Field [G]')

def get_data_point():
    data = s.readline()
    print(f"Incoming data: {data}")
    data = "".join([hex(x)[2:] for x in list(data)[:-1]])
    if data == 'b\'\\n\'':
        return 0
    Bt_squared = int(data, 16)
    Bt = math.sqrt(Bt_squared)
    print(f"Converted data: {Bt}")
    return Bt
    

ports = get_ports()
baud_rate = 115200
# define and open port
s = serial.Serial(ports[0].device, baud_rate) # default transaction size is 1 byte
if (not(s.is_open)):
    s.open()

while True:
    anim = animation.FuncAnimation(fig, animate, fargs=(time_axis, b_field), interval=750)
    plt.show()