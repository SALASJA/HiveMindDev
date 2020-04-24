import glob
import serial

ports = glob.glob("/dev/tty.wchusbserial*")
print(ports)
choice = int(input("enter you port choice: "))
port = ports[choice]
ser = None
try:
	collect = False
	ser = serial.Serial(port, 9600, timeout = 0)
	byte_buffer = bytearray()
	i = 0
	while True:
		byte = ser.read()
		if len(byte) > 0:
			byte_array.append(byte)
			 
			
		if len(byte) == 0 and collect:
			print('\n\n\n\n\n\n\n\n\n\n\n')
			collect = False

except Exception as e:
	print(e)
	
finally:
	if ser != None:
		ser.close()

