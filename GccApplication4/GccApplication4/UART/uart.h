#ifndef UART_H
#define UART_H

#include <avr/io.h>
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


#endif