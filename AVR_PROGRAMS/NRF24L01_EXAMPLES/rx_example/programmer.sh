currentport=$(ls /dev/cu.wchusbserial*) 
avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o main.o main.cpp
avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o nrf24.o ../nrf24.cpp
avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o radioPinFunctions.o radioPinFunctions.cpp
avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o I2C.o ../I2C.cpp
avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o SSD1306.o ../SSD1306.cpp
avr-gcc -Os -DF_CPU=16000000UL -mmcu=ATmega328P -c -o Framebuffer.o ../Framebuffer.cpp
avr-gcc -mmcu=ATmega328P I2C.o SSD1306.o Framebuffer.o main.o nrf24.o radioPinFunctions.o -o wireless
avr-objcopy -O ihex -R .eeprom wireless wireless.hex
avrdude -V -F -p ATmega328P -P $currentport -c stk500v1 -b 115200 -U flash:w:wireless.hex