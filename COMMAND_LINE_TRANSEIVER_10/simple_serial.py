import serial
import glob
import io
import time
import multiprocessing
import curses

ports = glob.glob("/dev/tty.wchusbserial*")[0]
all_ports =  glob.glob("/dev/tty.wchusbserial*")
print(all_ports)

# this port address is for the serial tx/rx pins on the GPIO header
SERIAL_PORT = ports
# be sure to set this to the same rate used on the Arduino
SERIAL_RATE = 9600


def printing(ser):
	while True:
		reading = ser.readline()
		print(reading)

def main():
    ser = None
    p1 = None
    try:
    	ser = serial.Serial(SERIAL_PORT, SERIAL_RATE)
    	p1 = multiprocessing.Process(target = printing, args = (ser,))
    	p1.start()		
    	while True:
				word = input("Enter a message to write:")
				ser.write(bytes(" " + word + "\n", encoding ='utf-8'))
    except:
    	pass
    finally:
    	p1.terminate()
    	ser.close()
    	

if __name__ == "__main__":
	main()

# using ser.readline() assumes each line contains a single reading
# sent using Serial.println() on the Arduino
#reading = ser.readline().decode('utf-8')
# reading is a string...do whatever you want from here
#print(reading)