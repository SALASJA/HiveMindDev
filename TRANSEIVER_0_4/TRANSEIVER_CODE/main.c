/*
	HIVEMIND Project edits
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
uint8_t tx_address[5] = {0xE7,0xE7,0xE7,0xE7,0xE7};
uint8_t rx_address[5] = {0xD7,0xD7,0xD7,0xD7,0xD7};
char success[32] = "<<<success>>>";
char prev_data[32];

void left_shift(uint8_t * data_buffer);
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

uint8_t print_address(uint8_t * address){
	printf("ADDRESS:");
	for(uint8_t i = 0; i < 5; i++){
		USART_Transmit(address[i]);
	}
	USART_Transmit('\n');
}

void setTransmitterAddress(uint8_t * new_address){
	for(uint8_t i = 0; i < 5; i++){
		tx_address[i] = new_address[i + 1];
	}
	nrf24_tx_address(tx_address);
	print_address(tx_address);
}

void setReceiverAddress(uint8_t * new_address){
	for(uint8_t i = 0; i < 5; i++){
		rx_address[i] = new_address[i + 1];
	}
    nrf24_rx_address(rx_address);
	print_address(rx_address);
}

void left_shift(uint8_t * data_buffer){
	for(int i = 1; i < 32; i++){
		data_buffer[i - 1] = data_buffer[i];
	}
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
		switch(data_buffer[0]){
			case '0': {
					  left_shift(data_buffer);
					  nrf24_send(data_buffer); //maybe I should edit esto instead
					  while(nrf24_isSending())
					  	;
					} break;
					
			case '1':   setTransmitterAddress(data_buffer);
					  break;
			case '2':   setReceiverAddress(data_buffer);	
					  break;
			case '3':   print_address(tx_address);	
					  break;
			case '4':   print_address(rx_address);
			          break;
			default:  printf("INVALID STATE\n");
					
		}
		//nrf24_send(data_buffer); /* Automatically goes to TX mode */
		//while(nrf24_isSending()) /* Wait for transmission to end */
		//	;
		receiving = FALSE; 

	}
	sei();
}

