#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>
#include "../UART/uart.h"

//^^^relative file position to uart header
//use programmer.sh to program with avr-gcc compiler
//directly with "bash programmer.sh"
//go to https://www.linkedin.com/pulse/introduction-avr-c-programming-macos-finally-attiny85-jorge-salas/?trackingId=ZUBziTtZSbuvwqTwPRXbvw%3D%3D
//to learn more about AVR programming on MAC
//Use Atmel studio if you have a windows PC
//Linux may also have AVR crosspack tools as well

#define TRUE 1
#define FALSE 0


void main(){
	USART_Init(); //sets up USART registers
	uint8_t * string = "It Works!\n";
	uint8_t i;
	while(TRUE){
		for(i = 0; string[i] != '\0'; i++){
			USART_Transmit(string[i % 10]); //transmitting a byte to serial port
		}
		_delay_ms(2000); //delay 2 seconds per transmission
	}
}

//transmitting a byte to serial port, any programming language can read from the port
//in this case will be using python