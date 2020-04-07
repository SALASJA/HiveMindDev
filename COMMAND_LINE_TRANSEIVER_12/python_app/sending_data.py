import glob
from model_collection import *
import time
def main():
    ports = glob.glob("/dev/tty.wchusbserial*")
    if(len(ports) == 0):
    	print("no ports available, program ending")
    	exit()
    print(ports)
    choice = int(input("choose port to open (enter 0 to " + str(len(ports)- 1)  + "):"))
    serial_port_name = ports[choice]
    #SERIAL_RATE = 9600
    transeiver = None
    transeiver = MasterTransceiverInterface(SERIAL_PORT_NAME = serial_port_name) #it locks up because stdin is closed it needs to be opened I thin
    #possible error in command line transeiver, string the strings adds more bytes x3333333 thats whty X.X
    #need to add better error testing
    i = 0
    while True:
    	if i < 255:
    		transeiver.send(Command.personal_message(chr(i),str(i),transeiver.get_RX_address(0)))
    		i = i + 1
    		time.sleep(0.10)
    	else:
    		i = 0
    transeiver.close()

if __name__ == "__main__":
	main()