from time import sleep
import serial

ser = serial.Serial("/dev/tty.usbserial-1410") # establish connection on specific port
counter = 32 # below 32 everything in ASCII is gibberish

while True:
	counter += 1
	ser.write(str(chr(counter)))
	ser.readline() # read new output from Arduino
	sleep(.1) #delay for one tenth of a second
	if counter == 255:
		counter = 32