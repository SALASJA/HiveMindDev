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
 
#include <stdio.h>
#include <stdlib.h>
#include <avr/io.h>
#include <stdint.h>
#include <util/delay.h>
#include "../NRF24L01/nrf24.h"
#include "main.h"
#include "../UART/uart.h"


void copy(char * string, uint8_t * data_array);
void copy_s(uint8_t * data_array, char * string);

int main()
{
	uart_init();
    stdout = &uart_output;
    stdin  = &uart_input;
	uint8_t temp;
	uint8_t q = 0;
	char data_array_s[32];
	uint8_t data_array[32];
	uint8_t tx_address[5] = {0xE7,0xE7,0xE7,0xE7,0xE7};
	uint8_t rx_address[5] = {0xD7,0xD7,0xD7,0xD7,0xD7};
    
    /* init hardware pins */
    nrf24_init();
    
    /* Channel #2 , payload length: 4 */
    nrf24_config(2,32);

    /* Set the device addresses */
    nrf24_tx_address(tx_address);
    nrf24_rx_address(rx_address);    

    while(1)
    {                
        /* Fill the data buffer */
        
        scanf("%c%*c", data_array_s);
        scanf("%30[0-9a-zA-Z ]", data_array_s);                                 
		
        /* Automatically goes to TX mode */
        copy(data_array_s, data_array); 
        nrf24_send(data_array);        
        
        /* Wait for transmission to end */
        while(nrf24_isSending());

        /* Make analysis on last tranmission attempt */
        temp = nrf24_lastMessageStatus();


        
		/* Retranmission count indicates the tranmission quality */
		temp = nrf24_retransmissionCount();
		

		/* Optionally, go back to RX mode ... */
		nrf24_powerUpRx();
		while(!nrf24_dataReady())
        nrf24_getData(data_array);
        copy_s(data_array,data_array_s);
        printf("%s\n", data_array_s);

        
        

		/* Or you might want to power down after TX */
		// nrf24_powerDown();            

		/* Wait a little ... */
		_delay_ms(10);
    }
}

void copy_s(uint8_t * data_array, char * string){
	uint8_t i = 0;
	for(int i = 0; i < 31; i++){
		string[i] = data_array[i];
	}
	string[31] = 0; 
	
	
}

void copy(char * string, uint8_t * data_array){
	uint8_t i = 0;
	while(string[i] != '\0'){
		data_array[i] = string[i];
		i++;
	}
	data_array[i] = string[i];
	
}
