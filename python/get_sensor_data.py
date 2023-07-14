import serial
import serial.tools.list_ports

def get_ports():
    return serial.tools.list_ports.comports()

ports = get_ports()
baud_rate = 115200
print(ports[0].device)

# define and open port
s = serial.Serial(ports[0].device, baud_rate) # default transaction size is 1 byte
if (not(s.is_open)):
    s.open()

while True:
    data = s.readline()
    data = data.decode('utf-8')
    
    print(data)