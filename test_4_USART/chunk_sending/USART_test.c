#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>
#include <avr/interrupt.h>
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

uint8_t i = 0;

void main(){
	USART_Init(); //sets up USART registers
	DDRB |= 1 << 5; //sets arduino pin 13 to output
	sei();
	while(TRUE){
		; // stand alone semicolon is a NOP operation
	}
}

ISR(USART_RX_vect){
	uint8_t receivedByte;
	receivedByte = (uint8_t) USART_Receive();
	i++;
	if(i == 32){
		PORTB ^= 1 << 5; //toggles pin 13
		i = 0;
	}
	sei();
}
//receiving a byte from serial port, any programming language can send into the port
//in this case will be using python