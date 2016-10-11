import serial

from config import port

# Arduino hook
try:
    arduino = serial.Serial(port, 9600, timeout=0)
except:
    print "No arduino detected, please connect to COM6"
    exit()
