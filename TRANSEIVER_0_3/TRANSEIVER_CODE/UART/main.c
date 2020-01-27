#include <avr/io.h>
#include <avr/interrupt.h>
#include "uart.h"
#define FALSE 0
#define TRUE 1

unsigned char data_buffer[32];
uint8_t i = 0;
uint8_t is_full = FALSE;

int main (void)
{
	USART_Init();
	sei(); // Enable the Global Interrupt Enable flag so that interrupts can be processed, needed so interrupts can happen
	for (;;) // Loop forever
	{
		//printf("hmmmmm\n");
			 // Do nothing - echoing is handled by the ISR instead of in the main loop
	}   
}

ISR(USART_RX_vect)
{
	unsigned char receivedByte;
	receivedByte = USART_Receive(); // Fetch the received byte value into the variable "ByteReceived"
	data_buffer[i] = receivedByte;
	if(i < 31 && receivedByte == '\r'){
		print_newline();
	}
	else{
		USART_Transmit(receivedByte);
	}
	i++;
	if(i == 31 || receivedByte == '\r'){
		data_buffer[i] = 0;
		if(i == 31){
			is_full = TRUE;
		}
		i = 0;
		USART_Transmit_line(data_buffer);
		if(is_full){
			print_newline();
			is_full = FALSE;
		}
		
	}
	sei();
}