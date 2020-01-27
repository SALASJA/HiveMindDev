#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdio.h>
#include <stddef.h>

#ifndef F_CPU
#define F_CPU 16000000UL
#endif

#ifndef BAUD
#define BAUD 9600
#endif

#include <util/setbaud.h>


//#define BAUD_PRESCALE (((F_CPU / (UBRRH_VALUE * 16UL))) - 1)
#define USART_Data_Register_Empty() (UCSR0A & (1<<UDRE0)) // UCSRnA – USART Control and Status Register n A and USART Data Register Empty
#define USART_Receive_Complete() (UCSR0A & (1<<RXC0))

void USART_Init();
unsigned char USART_Receive();
void USART_Transmit(unsigned char data);
void USART_Transmit_line(unsigned char * data_buffer);
void print_newline();

FILE  uart_output = FDEV_SETUP_STREAM(USART_Transmit, NULL, _FDEV_SETUP_WRITE);
FILE  uart_input = FDEV_SETUP_STREAM(NULL, USART_Receive, _FDEV_SETUP_READ);

unsigned char data_buffer[32];
uint8_t i = 0;

int main (void)
{
	USART_Init();
	for (;;) // Loop forever
	{
		//printf("hmmmmm\n");
			 // Do nothing - echoing is handled by the ISR instead of in the main loop
	}   
}

void USART_Init()
{
	stdout = &uart_output;
	stdin  = &uart_input;
	UBRR0H = UBRRH_VALUE;
    UBRR0L = UBRRL_VALUE;
    UCSR0A &= ~(_BV(U2X0));
	UCSR0C = _BV(UCSZ01) | _BV(UCSZ00); /* 8-bit data */ 
    UCSR0B = _BV(RXEN0) | _BV(TXEN0);   /* Enable RX and TX */  
    UCSR0B |= (1 << RXCIE0);// | (1 << TXCIE0); // Enable the USART Recieve Complete interrupt (USART_RXC)
	sei(); // Enable the Global Interrupt Enable flag so that interrupts can be processed
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
	if (data == '\n') {
        USART_Transmit('\r');
    }
	while (!USART_Data_Register_Empty()) //USART_Data_Register_Empty (UCSRnA & (1<<UDREn))
		;
	/* Put data into buffer, sends the data */
	UDR0 = data;
}


void USART_Transmit_line(unsigned char * data_buffer){
	uint8_t j = 0;
	while(data_buffer[j] != '\0'){
		USART_Transmit(data_buffer[j]);
		j++;
	}
}
void print_newline(){
	USART_Transmit('\n');
	USART_Transmit('\n');
	USART_Transmit('\r');
	USART_Transmit('\r');
}


ISR(USART_RX_vect)
{
	unsigned char receivedByte;
	receivedByte = USART_Receive(); // Fetch the received byte value into the variable "ByteReceived"
	data_buffer[i] = receivedByte;
	if(i == 0 && receivedByte == '\n'){
		print_newline();
	}
	USART_Transmit(receivedByte);
	i++;
	if(i == 31 || receivedByte == '\n'){
		data_buffer[i] = 0;
		i = 0;
		print_newline();
		USART_Transmit_line(data_buffer);
		print_newline();
	}
	//USART_Transmit(ReceivedByte); // Echo back the received byte back to the computer
	sei();
}
