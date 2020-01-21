currentport=$(ls /dev/cu.wchusbserial*) 
avr-gcc -Os -DF_CPU=16000000UL -fpermissive -mmcu=ATmega328P -c -o I2C.o ../SSD1306/I2C.cpp
avr-gcc -Os -DF_CPU=16000000UL -fpermissive -mmcu=ATmega328P -c -o uart.o ../UART_CPP/src/uart.cc
avr-gcc -Os -DF_CPU=16000000UL -fpermissive -mmcu=ATmega328P -c -o SSD1306.o ../SSD1306/SSD1306.cpp
avr-gcc -Os -DF_CPU=16000000UL -fpermissive -mmcu=ATmega328P -c -o Framebuffer.o ../SSD1306/Framebuffer.cpp
avr-gcc -Os -DF_CPU=16000000UL  -fpermissive -mmcu=ATmega328P -c -o movepixel.o movepixel.cpp
avr-gcc -mmcu=ATmega328P I2C.o SSD1306.o Framebuffer.o movepixel.o -o movepixel
avr-objcopy -O ihex -R .eeprom movepixel movepixel.hex
avrdude -V -F -p ATmega328P -P $currentport -c stk500v1 -b 115200 -U flash:w:movepixel.hex
#""
