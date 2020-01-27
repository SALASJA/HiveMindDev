/*
 * Demonstration on how to redirect stdio to UART. 
 *
 * http://appelsiini.net/2011/simple-usart-with-avr-libc
 *
 * To compile and upload run: make clean; make; make program;
 * Connect to serial with: screen /dev/tty.usbserial-*
 *
 * Copyright 2011 Mika Tuupola
 *
 * Licensed under the MIT license:
 *   http://www.opensource.org/licenses/mit-license.php
 *
 */
 
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <util/delay.h>
#include "../NRF24L01/nrf24.h"
#include "../UART_Finalized/uart.h"

#define TRUE 1
#define FALSE 0

uint8_t receive_buffer[32];
uint8_t data_buffer[32];
uint8_t data_buffer_index = 0;
uint8_t rx_address_index = 0;
uint8_t tx_address_index = 0;
uint8_t receiving = FALSE;
uint8_t change_mode = TRUE;
uint8_t SENDING = FALSE;
uint8_t mode_number = '0';
uint8_t tx_address[5] = {0xE7,0xE7,0xE7,0xE7,0xE7};
uint8_t rx_address[5] = {0xD7,0xD7,0xD7,0xD7,0xD7};
void collect_and_transmit();
void setTransmitterAddress();
void setReceiverAddress();
void getNodeState();
void setNodeState();
void print_address(uint8_t * address);

int main()
{
	USART_Init();
	//uint8_t tx_address[5] = {0xE7,0xE7,0xE7,0xE7,0xE7};
	//uint8_t rx_address[5] = {0xD7,0xD7,0xD7,0xD7,0xD7};
    
    /* init hardware pins */
    nrf24_init();
    
    /* Channel #2 , payload length: 4 */
    nrf24_config(2,32);

    /* Set the device addresses */
    nrf24_tx_address(tx_address);
    nrf24_rx_address(rx_address);
    sei();    

    while(1)
    {                
		/* Optionally, go back to RX mode ... */
		if(!receiving){
			nrf24_powerUpRx();
			receiving = TRUE;
		}
		if(nrf24_dataReady()){
        	nrf24_getData(receive_buffer);
        	printf("RECEIVED:%s\n",receive_buffer); //bytes 0-9 need to be removed by program
        }
		/* Or you might want to power down after TX */
		// nrf24_powerDown();            
		/* Wait a little ... */
		_delay_ms(10);
    }
}

void collect_and_transmit(){
	SENDING = TRUE;
	uint8_t receivedByte;
	receivedByte = (uint8_t) USART_Receive(); // Fetch the received byte value into the variable "ByteReceived"
	
	data_buffer[data_buffer_index] = receivedByte;
	/*
	if(data_buffer_index < 31 && receivedByte == '\r'){
		print_newline();
	}
	else{
			USART_Transmit(receivedByte);
	}*/
	data_buffer_index++;
	
	if(data_buffer_index == 31 || receivedByte == '\r'){
		/*
		if(i == 1 && receivedByte == '\r'){
			i = 0;
		}*/
		data_buffer[data_buffer_index] = 0;
		data_buffer_index = 0;
		nrf24_send(data_buffer); /* Automatically goes to TX mode */
		while(nrf24_isSending()) /* Wait for transmission to end */
			;
		
		/* Make analysis on last tranmission attempt */
		//temp = nrf24_lastMessageStatus();
		/* Retranmission count indicates the tranmission quality */
		//temp = nrf24_retransmissionCount();
		printf("sent\n");
		receiving = FALSE;
		SENDING = FALSE;
	}
}

void setTransmitterAddress(){
	uint8_t receivedByte;
	receivedByte = (uint8_t) USART_Receive(); // Fetch the received byte value into the variable "ByteReceived"
	tx_address[tx_address_index] = receivedByte;
	tx_address_index++;
	if(tx_address_index == 5){
		tx_address_index = 0;
		mode_number = '0';
		USART_Receive();
	}
	
}

void setReceiverAddress(){
	uint8_t receivedByte;
	receivedByte = (uint8_t) USART_Receive(); // Fetch the received byte value into the variable "ByteReceived"
	rx_address[rx_address_index] = receivedByte;
	rx_address_index++;
	if(rx_address_index == 5){
		rx_address_index = 0;
		mode_number = '0';
		USART_Receive();
	}
}

void getNodeState(){
	uint8_t receivedByte;
	receivedByte = (uint8_t) USART_Receive(); // Fetch the received byte value into the variable "ByteReceived"
	switch(receivedByte){
		case '0': print_address(tx_address);
				break;
		case '1': print_address(rx_address);
				break;
		
		default: printf("STATE:invalid state\n");
	}
	USART_Receive();
	mode_number = '0';
}

void print_address(uint8_t * address){
	for(int i = 0; i < 5; i++){
		USART_Transmit(address[i]);
	}
	USART_Transmit('\n');
}



ISR(USART_RX_vect) //its a lot like a GUI event if you have worked with those, maybe i need to add the backspace feature for those who dont want a gui
{	
	SENDING = TRUE;
	uint8_t receivedByte;
	receivedByte = (uint8_t) USART_Receive(); // Fetch the received byte value into the variable "ByteReceived"
	
	data_buffer[data_buffer_index] = receivedByte;
	/*
	if(data_buffer_index < 31 && receivedByte == '\r'){
		print_newline();
	}
	else{
			USART_Transmit(receivedByte);
	}*/
	data_buffer_index++;
	
	if(data_buffer_index == 31 || receivedByte == '\r'){
		/*
		if(i == 1 && receivedByte == '\r'){
			i = 0;
		}*/
		data_buffer[data_buffer_index] = 0;
		data_buffer_index = 0;
		nrf24_send(data_buffer); /* Automatically goes to TX mode */
		while(nrf24_isSending()) /* Wait for transmission to end */
			;
		/* Make analysis on last tranmission attempt */
		//temp = nrf24_lastMessageStatus();
		/* Retranmission count indicates the tranmission quality */
		//temp = nrf24_retransmissionCount();
		printf("sent\n");
		receiving = FALSE;
		SENDING = FALSE;
	}
	sei();
}

/*
//!n is for mode change, ' ' a space is no changing, 
ISR(USART_RX_vect) //its a lot like a GUI event if you have worked with those, maybe i need to add the backspace feature for those who dont want a gui
{	
	uint8_t receivedByte;
	if(!SENDING){
		receivedByte = (uint8_t) USART_Receive();
		printf("MODE:%c\n",receivedByte);
	}
	if(!SENDING && receivedByte == '!'){
		receivedByte = (uint8_t) USART_Receive();
		printf("MODE:%c\n",receivedByte);
		if('0' <= receivedByte && receivedByte <= '3'){
			mode_number = receivedByte;
			printf("MODE:%c\n",mode_number);
		}
	}
		
	switch(mode_number){
		case '0': collect_and_transmit();
		          break;
		case '1': setTransmitterAddress();
				  break;
		case '2': setReceiverAddress();
				  break;
		case '3': getNodeState();
				  break;
		default:  printf("MODE:Invalid Mode\n");
	}
	sei();
}*/