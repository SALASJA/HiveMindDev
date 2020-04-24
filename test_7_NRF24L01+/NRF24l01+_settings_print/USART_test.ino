#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>

extern "C"{
  #include <uart.h>
}
//^^^ this is important because .ino is technically C++, this is needed to link C file properly
//^^^ UART folder needs to be dragged into libraries folder in Arduino folder in documents
//copy code and paste it into a new arduino (within the IDE) file if forces to make  a folder

#define TRUE 1
#define FALSE 0

void setup(){
	USART_Init(); //sets up USART registers
	uint8_t * string = "It Works!\n";
	uint8_t i;
}

void loop(){
	USART_Transmit(10); //the size of the message I am sending
	for(i = 0; string[i] != '\0'; i++){
		USART_Transmit(string[i % 10]); //transmitting a byte to serial port
	}
	_delay_ms(2000); //delay 2 seconds per transmission
}

//transmitting a byte to serial port, any programming language can read from the port
//in this case will be using python