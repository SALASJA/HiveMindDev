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
#define toggle_success_mode(x) x = !x

uint8_t receive_buffer[32];
uint8_t data_buffer[32];
uint8_t data_buffer_index = 0;
uint8_t receiving = FALSE;
uint8_t tx_address[5] = {'?','?','?','?','?'};
uint8_t rx_address[5] = {'!','!','!','!','!'};
uint8_t success_mode = FALSE;         //I feel success mode should automatically be off
char success[32] = "<<<success>>>";//13
char prev_data[32];

void left_shift(uint8_t * data_buffer);
uint8_t is_success(uint8_t * recieve);
uint8_t print_address(uint8_t * address);
void setTransmitterAddress(uint8_t * new_address);
void setReceiverAddress(uint8_t * new_address);

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
	DDRD |= (1 << 5); //can comment out these lines but can now give us insight on external controll
    while(1)
    {                
		/* Optionally, go back to RX mode ... */
		if(!receiving){
			nrf24_powerUpRx();
			receiving = TRUE;
		}
		if(nrf24_dataReady()){
			nrf24_getData(receive_buffer);
			if(receive_buffer[0] == '1' || receive_buffer[0] == '1'){ // this might have to be a separate library
				PORTD ^= 1 << 5;
			}
			if(success_mode){
				if(is_success(receive_buffer)){
					printf("SUCCESS:%s\n",success);
				}else{
					printf("RECEIVED:%s\n",receive_buffer); //bytes 0-9 need to be removed by program
					for(uint8_t i = 0; i < 5; i++){
						success[13 + i] = rx_address[i];
					}
					success[18] = (PIND & (1 << 5)) + 48;
					success[19] = 0;
					nrf24_send(success);
					receiving = FALSE;
				}
        	}
        	else{
				printf("RECEIVED:%s\n",receive_buffer);
        	}
        	
        }
		/* Or you might want to power down after TX */
		// nrf24_powerDown();            
		/* Wait a little ... */
		_delay_ms(10);
    }
}

uint8_t is_success(uint8_t * receive){
	uint8_t i;
	for(i = 0; i < 13; i++){
		if(receive[i] != success[i]){
			return FALSE;
		}
	}
	return TRUE;
}

uint8_t print_address(uint8_t * address){
	printf("STATE:");
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
}

void setReceiverAddress(uint8_t * new_address){
	for(uint8_t i = 0; i < 5; i++){
		rx_address[i] = new_address[i + 1];
	}
    nrf24_rx_address(rx_address);
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
					  } 
					  break;
					
			case '1': setTransmitterAddress(data_buffer);
					  break;
			case '2': setReceiverAddress(data_buffer);	
					  break;
			case '3': print_address(tx_address);	
					  break;
			case '4': print_address(rx_address);
			          break;
			case '5': toggle_success_mode(success_mode);
					  break;
			case '6': { //get success mode
						printf("STATE:");
						USART_Transmit(success_mode + '0');
						USART_Transmit('\n');
					  }
					  break;
			case '7': PORTD ^= 1 << 5;    //getting the state of whether a port is on would be cool, this is where stron designing of the c code will come on
					  break;
			case '8': //in python program this is for discover mode this is not meant to be implemented here
			          break;
			case '9': // in python program this is for finding mode, again not to be implemented
					  break; // will add a polling mode I think a separate pipe should be dedicated for that
					  
			default:  printf("INVALID STATE\n");
					
		}
		//nrf24_send(data_buffer); /* Automatically goes to TX mode */
		//while(nrf24_isSending()) /* Wait for transmission to end */
		//	;
		receiving = FALSE; 

	}
	sei();
}

