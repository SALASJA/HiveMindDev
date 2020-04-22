import glob
from master_transceiver_interface import MasterTransceiverInterface
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
    transeiver.start_threads()
    message = input("Enter a message to write:")
    while message != 'x':
    	transeiver.command_line_send(message)
    	message = input("Enter a message to write:")
    transeiver.close()

if __name__ == "__main__":
	main()