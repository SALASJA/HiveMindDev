avr-gcc -Os -DF_CPU=1000000 -mmcu=attiny85 -c -o main.o main.c
avr-gcc -Os -DF_CPU=1000000 -mmcu=attiny85 -c -o radioPinFunctions.o radioPinFunctions.c 
avr-gcc -Os -DF_CPU=1000000 -mmcu=attiny85 -c -o nrf24-noce.o lib/nrf24-noce.c
avr-gcc -DF_CPU=1000000 -mmcu=attiny85 nrf24-noce.o  radioPinFunctions.o main.o  -o main
avr-objcopy -O ihex main main.hex
avrdude -c usbtiny -p attiny85 -U flash:w:main.hex