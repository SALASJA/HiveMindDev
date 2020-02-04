#include "uart.h"


//these top two the most import lines 
FILE  uart_output = FDEV_SETUP_STREAM(USART_Transmit, NULL, _FDEV_SETUP_WRITE);
FILE  uart_input = FDEV_SETUP_STREAM(NULL, USART_Receive, _FDEV_SETUP_READ);
//extern unsigned char data_buffer[];
//extern uint8_t i;

void USART_Init()
{
	stdout = &uart_output;
	stdin  = &uart_input;
	UBRR0H = UBRRH_VALUE;
    UBRR0L = UBRRL_VALUE;
    UCSR0A &= ~(_BV(U2X0));
	UCSR0C = _BV(UCSZ01) | _BV(UCSZ00); /* 8-bit data */ 
    UCSR0B = _BV(RXEN0) | _BV(TXEN0);   /* Enable RX and TX */  
    UCSR0B |= (1 << RXCIE0);// | (1 << TXCIE0); // Enable the USART Recieve Complete interrupt (USART_RXC), its like GUI event but for microcontrollers
}


unsigned char USART_Receive()
{
	/* Wait for data to be received */
	while (!USART_Receive_Complete()) //USART_Receive_Complete (UCSRnA & (1<<RXCn))
		;
	/* Get and return received data from buffer */
	return UDR0;
}


void USART_Transmit(unsigned char data)
{
	/* Wait for empty transmit buffer */
	//if (data == '\n') {
    //   USART_Transmit('\r');
    //}
	while (!USART_Data_Register_Empty()) //USART_Data_Register_Empty (UCSRnA & (1<<UDREn))
		;
	/* Put data into buffer, sends the data */
	UDR0 = data;
}


void USART_Transmit_line(unsigned char * data){
	uint8_t j = 0;
	while(data[j] != '\0'){
		USART_Transmit(data[j]);
		j++;
	}
	print_newline();
}
void print_newline(){
	USART_Transmit('\n');
	//USART_Transmit('\r');
	
}

/* example Interrupt, paste in main file to watch it work
#include <avr/interrupt.h>
unsigned char data_buffer[32];
uint8_t i = 0;
uint8_t is_full = FALSE;

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
*/

