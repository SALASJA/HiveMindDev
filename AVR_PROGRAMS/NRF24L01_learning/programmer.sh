avr-gcc -g -Os -DF_CPU=1000000 -mmcu=attiny85 -c -o nrf24_tiny.o nrf24_tiny2.c
avr-gcc -g -Os -DF_CPU=1000000 -mmcu=attiny85 nrf24_tiny.o  -o nrf24_tiny.elf
avr-objcopy -O ihex nrf24_tiny.elf nrf24_tiny.hex
avrdude -c usbtiny -p attiny85 -U flash:w:nrf24_tiny.hex