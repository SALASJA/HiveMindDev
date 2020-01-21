currentport=$(ls /dev/cu.wchusbserial*) 
avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o main.o main.c
avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o nrf24.o ../nrf24.c
avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o xprintf.o util/xprintf.c
avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o radioPinFunctions.o radioPinFunctions.c
avr-gcc -mmcu=ATmega328P main.o nrf24.o xprintf.o radioPinFunctions.o -o wireless
avr-objcopy -O ihex -R .eeprom wireless wireless.hex
avrdude -V -F -p ATmega328P -P $currentport -c stk500v1 -b 115200 -U flash:w:wireless.hex