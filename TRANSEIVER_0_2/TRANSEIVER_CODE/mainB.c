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
#include "NRF24L01/nrf24.h"
#include "UART/uart.h"

#define TRUE 1
#define FALSE 0

uint8_t receive_buffer[32];
uint8_t data_buffer[32];
uint8_t data_buffer_index = 0;
uint8_t receiving = FALSE;
uint8_t rx_address[5] = {0xE7,0xE7,0xE7,0xE7,0xE7};
uint8_t tx_address[5] = {0xD7,0xD7,0xD7,0xD7,0xD7};
char success[32] = "<<<success>>>";
char prev_data[32];

uint8_t is_success(uint8_t * recieve);

int main()
{
	USART_Init();
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
        	if(is_success(receive_buffer)){
        		printf("SUCCESS:%s\n",success);
        	}else{
        		printf("RECEIVED:%s\n",receive_buffer); //bytes 0-9 need to be removed by program
        		nrf24_send(success);
        	}
        	receiving = FALSE;
        }
		/* Or you might want to power down after TX */
		// nrf24_powerDown();            
		/* Wait a little ... */
		_delay_ms(10);
    }
}

uint8_t is_success(uint8_t * receive){
	uint8_t i = 0;
	while(success[i] != '\0'){
		if(receive[i] != success[i]){
			return FALSE;
		}
		i++;
	}
	return TRUE;
}


ISR(USART_RX_vect) //its a lot like a GUI event if you have worked with those, maybe i need to add the backspace feature for those who dont want a gui
{	
	uint8_t receivedByte;
	receivedByte = (uint8_t) USART_Receive(); // Fetch the received byte value into the variable "ByteReceived"
	data_buffer[data_buffer_index] = receivedByte;
	data_buffer_index++;
	if(data_buffer_index == 31 || receivedByte == '\r'){
		data_buffer[data_buffer_index] = 0;
		data_buffer_index = 0;
		nrf24_send(data_buffer); /* Automatically goes to TX mode */
		while(nrf24_isSending()) /* Wait for transmission to end */
			;
		receiving = FALSE; 

	}
	sei();
}

