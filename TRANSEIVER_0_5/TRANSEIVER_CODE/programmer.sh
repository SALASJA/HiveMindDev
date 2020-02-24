currentport=( $(ls /dev/cu.wchusbserial*) )
n=$((${#currentport[@]}-1))
for i in $(seq 0 $n)
do
	printf "PROGRAMMING BOARD ON PORT %s\n" ${currentport[i]}
	avr-g++ -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o main.o main.cpp
	avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o uart.o UART/uart.c
	avr-g++ -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o nrf24.o NRF24L01/nrf24.cpp
	avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o spi.o SPI/spi.c
	avr-g++ -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o util.o UTIL/util.cpp
	avr-g++ -mmcu=ATmega328P main.o util.o uart.o nrf24.o spi.o -o main
	avr-objcopy -O ihex -R .eeprom main main.hex
	avrdude -V -F -p ATmega328P -P ${currentport[i]} -c stk500v1 -b 115200 -U flash:w:main.hex:i
	#/Applications/Arduino.app/Contents/Java/hardware/tools/avr/bin/avrdude -C/Applications/Arduino.app/Contents/Java/hardware/tools/avr/etc/avrdude.conf -v -patmega328p -carduino -P/dev/cu.wchusbserial1420 -b57600 -D -Uflash:w:${mainshex[i]}:i 
	#the above line is what extracted from arduino IDE's compilation, for some reason some boards need to be programmed like this
done
