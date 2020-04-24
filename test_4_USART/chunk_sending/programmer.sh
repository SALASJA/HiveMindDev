currentport=( $(ls /dev/cu.wchusbserial*) )
n=$((${#currentport[@]}-1))
for i in $(seq 0 $n)
do
	printf "PROGRAMMING BOARD ON PORT %s\n" ${currentport[i]}
	avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o USART_test.o USART_test.c
	avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o uart.o ../UART/uart.c #folder up one level
	avr-gcc -mmcu=ATmega328P USART_test.o  uart.o -o main
	avr-objcopy -O ihex -R .eeprom main main.hex
	avrdude -V -F -p ATmega328P -P ${currentport[i]} -c stk500v1 -b 115200 -U flash:w:main.hex:i
done
