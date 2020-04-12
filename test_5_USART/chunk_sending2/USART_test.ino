#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>
#include <avr/interrupt.h>

extern "C"{
  #include <uart.h>
}
//^^^ this is important because .ino is technically C++, this is needed to link C file properly
//^^^ UART folder needs to be dragged into libraries folder in Arduino folder in documents
//copy code and paste it into a new arduino (within the IDE) file if forces to make  a folder
uint8_t equals(uint8_t * A, uint8_t * B);

#define TRUE 1
#define FALSE 0

uint8_t i = 0;
uint8_t success[] = {'s','u','c','c','e','s','s'};
uint8_t buffer[32];

void setup(){
	USART_Init(); //sets up USART registers
	DDRB |= 1 << 5; //sets arduino pin 13 to output 
	sei()
}

void loop(){

}

ISR(USART_RX_vect){
	uint8_t receivedByte;
	receivedByte = (uint8_t) USART_Receive();
	buffer[i] = receivedByte;
	i++;
	if(i == 32){
		if(equals(success,buffer)){
			PORTB ^= 1 << 5; //toggles pin 13
		}
		i = 0;
	}
	sei();//every time its called, interrupt is cleared so need to set it again =
}

//receiving 32 bytes from serial port, any programming language can send into the port
//in this case will be using python

uint8_t equals(uint8_t * A, uint8_t * B){
	for(uint8_t j = 0; j < 7; j++){
		if(A[j] != B[j]){
			return FALSE;
		}
	}
	return TRUE;
}