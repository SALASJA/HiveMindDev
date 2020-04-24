#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>

extern "C"{
	#include "../UART/uart.h"
}

#include "../NRF24L01/nrf24.h"

//^^^relative file position to uart header
//use programmer.sh to program with avr-gcc compiler
//directly with "bash programmer.sh"
//go to https://www.linkedin.com/pulse/introduction-avr-c-programming-macos-finally-attiny85-jorge-salas/?trackingId=ZUBziTtZSbuvwqTwPRXbvw%3D%3D
//to learn more about AVR programming on MAC
//Use Atmel studio if you have a windows PC
//Linux may also have AVR crosspack tools as well

#define TRUE 1
#define FALSE 0

int main(){
	USART_Init(); //sets up USART registers
	Nrf24 transceiver;
	transceiver.init();
	static uint8_t buffer[5];
	while(TRUE){
		transceiver.readRegister(TX_ADDR, buffer, 5);    //gets address from transceiver
		USART_Transmit(5);
		for(uint8_t i = 0; i < 5; i++){
			USART_Transmit(buffer[i]); //transmitting a byte to serial port
		}
		_delay_ms(2000); //delay 2 seconds per transmission
	}
	return 0;
}

//transmitting a byte to serial port, any programming language can read from the port
//in this case will be using python
