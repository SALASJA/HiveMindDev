import glob
from transeiver_steven import *

def main():
    ports = glob.glob("/dev/tty.usbserial*")
    if(len(ports) == 0):
    	print("no ports available, program ending")
    	exit()
    print(ports)
    choice = int(input("choose port to open (enter 0 to " + str(len(ports)- 1)  + "):"))
    serial_port_name = ports[choice]
    #SERIAL_RATE = 9600
    #try:
    transeiver = MasterTranseiver(SERIAL_PORT_NAME = serial_port_name) #it locks up because stdin is closed it needs to be opened I think	
    while True:
    	word = input("Enter a message to write:")
    	transeiver.sendMessage(word)
    #except:	
    #	pass

if __name__ == "__main__":
	main()