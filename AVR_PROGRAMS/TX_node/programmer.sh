currentport=$(ls /dev/cu.wchusbserial*)
avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o main.o main.c
avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o uart.o ../UART/uart.c
avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o nrf24.o ../NRF24L01/nrf24.c
avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o radioPinFunctions.o ../NRF24L01/radioPinFunctions.c
avr-gcc -mmcu=ATmega328P main.o uart.o nrf24.o radioPinFunctions.o -o main
avr-objcopy -O ihex -R .eeprom main main.hex
avrdude -V -F -p ATmega328P -P $currentport -c stk500v1 -b 115200 -U flash:w:main.hex
