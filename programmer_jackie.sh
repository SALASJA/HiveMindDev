currentport=( $(ls /dev/cu.usbserial-*) )
n=$((${#currentport[@]}-1))
TX=TRANSEIVER_CODE
tool_D="/Users/jackiecuong/Downloads/Arduino/Contents/Java/hardware/tools/avr/bin"
conf_D="/Users/jackiecuong/Downloads/Arduino/Contents/Java/hardware/tools/avr/etc"
for i in $(seq 0 $n)
do
	printf "PROGRAMMING BOARD ON PORT %s\n" ${currentport[i]}
	$tool_D/avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o $TX/main.o $TX/main.c
	$tool_D/avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o $TX/uart.o $TX/UART/uart.c
	$tool_D/avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o $TX/nrf24.o $TX/NRF24L01/nrf24.c
	$tool_D/avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o $TX/radioPinFunctions.o $TX/NRF24L01/radioPinFunctions_rfnano.c
	$tool_D/avr-gcc -mmcu=ATmega328P $TX/main.o $TX/uart.o $TX/nrf24.o $TX/radioPinFunctions.o -o $TX/main
	$tool_D/avr-objcopy -O ihex -R .eeprom $TX/main $TX/main.hex
	#avrdude -V -F -p ATmega328P -P ${currentport[i]} -c stk500v1 -b 115200 -U flash:w:$TX/main.hex:i
	#/Applications/Arduino.app/Contents/Java/hardware/tools/avr/bin/avrdude -C/Applications/Arduino.app/Contents/Java/hardware/tools/avr/etc/avrdude.conf -v -patmega328p -carduino -P/dev/cu.wchusbserial1420 -b57600 -D -Uflash:w:${mainshex[i]}:i 
	#the above line is what extracted from arduino IDE's compilation, for some reason some boards need to be programmed like this
	$tool_D/avrdude -C/Users/jackiecuong/Downloads/Arduino/Contents/Java/hardware/tools/avr/etc/avrdude.conf -v -patmega328p -carduino -P/dev/cu.usbserial-1410 -b115200 -D -Uflash:w:$TX/main.hex:i 
done