import glob
from transceiver import *

def main():
    ports = glob.glob("/dev/tty.wchusbserial*") + glob.glob("/dev/tty.usbserial*") + glob.glob("COM5")
    if(len(ports) == 0):
    	print("no ports available, program ending")
    	exit()
    print(ports)
    choice = int(input("choose port to open (enter 0 to " + str(len(ports)- 1)  + "):"))
    serial_port_name = ports[choice]
    #SERIAL_RATE = 9600
    #try:
    transeiver = Transceiver(SERIAL_PORT_NAME = serial_port_name) #it locks up because stdin is closed it needs to be opened I think	
    while True:
    	word = input("Enter a message to write:")
    	transeiver.sendMessage(chr(ord(word[0]) - ord("0")) + word[1:])
    #except:	
    #	pass

if __name__ == "__main__":
	main()