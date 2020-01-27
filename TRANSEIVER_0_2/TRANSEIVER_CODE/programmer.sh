currentport=( $(ls /dev/cu.wchusbserial*) )
mains=(mainA.c mainB.c)
mainss=(mainA mainB)
mainso=(mainA.o mainA.b)
mainshex=(mainA.hex mainB.hex)
n=$((${#currentport[@]}-1))

for i in $(seq 0 $n)
do
	printf "PROGRAMMING BOARD ON PORT %s\n" ${currentport[i]}
	avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o ${mainso[i]} ${mains[i]}
	avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o uart.o UART/uart.c
	avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o nrf24.o NRF24L01/nrf24.c
	avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o radioPinFunctions.o NRF24L01/radioPinFunctions_rfnano.c
	avr-gcc -mmcu=ATmega328P ${mainso[i]} uart.o nrf24.o radioPinFunctions.o -o ${mainss[i]}
	avr-objcopy -O ihex -R .eeprom ${mainss[i]} ${mainshex[i]}
	avrdude -V -F -p ATmega328P -P ${currentport[i]} -c stk500v1 -b 115200 -U flash:w:${mainshex[i]}
done