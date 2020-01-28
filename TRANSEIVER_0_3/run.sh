currentport=( $(ls /dev/cu.wchusbserial*) )
mains=(mainA.c mainB.c)
mainss=(mainA mainB)
mainso=(mainA.o mainA.b)
mainshex=(mainA.hex mainB.hex)
n=$((${#currentport[@]}-1))

for i in $(seq 0 $n)
do
	printf "PROGRAMMING BOARD ON PORT %s\n" ${currentport[i]}
	avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o TRANSEIVER_CODE/${mainso[i]} TRANSEIVER_CODE/${mains[i]}
	avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o TRANSEIVER_CODE/uart.o TRANSEIVER_CODE/UART/uart.c
	avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o TRANSEIVER_CODE/nrf24.o TRANSEIVER_CODE/NRF24L01/nrf24.c
	avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o TRANSEIVER_CODE/radioPinFunctions.o TRANSEIVER_CODE/NRF24L01/radioPinFunctions_rfnano.c
	avr-gcc -mmcu=ATmega328P TRANSEIVER_CODE/${mainso[i]} TRANSEIVER_CODE/uart.o TRANSEIVER_CODE/nrf24.o TRANSEIVER_CODE/radioPinFunctions.o -o TRANSEIVER_CODE/${mainss[i]}
	avr-objcopy -O ihex -R .eeprom TRANSEIVER_CODE/${mainss[i]} TRANSEIVER_CODE/${mainshex[i]}
	avrdude -V -F -p ATmega328P -P ${currentport[i]} -c stk500v1 -b 115200 -U flash:w:TRANSEIVER_CODE/${mainshex[i]}
	#/Applications/Arduino.app/Contents/Java/hardware/tools/avr/bin/avrdude -C/Applications/Arduino.app/Contents/Java/hardware/tools/avr/etc/avrdude.conf -v -patmega328p -carduino -P/dev/cu.wchusbserial1420 -b57600 -D -Uflash:w:TRANSEIVER_CODE/${mainshex[i]}:i 
	#the above line is what extracted from arduino IDE's compilation, for some reason some boards need to be programmed like this
	
done

python3 NRF_GUI_APP_03.py &
python3 NRF_GUI_APP_03.py &