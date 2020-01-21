avr-gcc -Os -DF_CPU=1000000 -mmcu=attiny85 -c -o main.o main.c
avr-gcc -Os -DF_CPU=1000000 -mmcu=attiny85 -c -o nrf24.o ../NRF24L01/nrf24.c
avr-gcc -Os -DF_CPU=1000000 -mmcu=attiny85 -c -o radioPinFunctions.o ../NRF24L01/radioPinFunctions_tiny85.c
avr-gcc -mmcu=attiny85 main.o  nrf24.o radioPinFunctions.o -o main
avr-objcopy -O ihex -R .eeprom main main.hex
avrdude -c usbtiny -p attiny85 -U flash:w:main.hex
