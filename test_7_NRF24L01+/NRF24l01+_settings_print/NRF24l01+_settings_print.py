import serial
import glob

def main():
	"""
	under my mac /dev/tty.wchusbserial1410 is the port
	* <--- uses of regular expressions in cases of more
	than one connection
	"""
	ports = glob.glob("/dev/tty.wchusbserial*") + glob.glob("/dev/tty.usbserial*") + glob.glob("COM3") + glob.glob("COM4")
	BAUDRATE = 9600
	choice = int(input((str(ports) + " enter numerical index for port: ")))
	portname = ports[choice]
	port = None
	try:
		port = serial.Serial(portname, BAUDRATE, timeout = 0)
		while True:
			byteslist = get_byte_group(port)
			if len(byteslist) != 0: #successful transmission if positive bytes, must check because sometimes empty
				print("RECEIVED BYTES: ", byteslist)
	except Exception as e:
		print("ERROR:", e)
	finally:
		if port != None:
			port.close()


def get_byte_group(port):
	byte = port.read()
	byteslist = bytearray()
	if len(byte) > 0:
		length = byte[0]
		i = 0
		while i < length:
			byte = port.read()
			if len(byte) > 0:
				byteslist.append(byte[0])
				i = i + 1
	return byteslist
	
main()