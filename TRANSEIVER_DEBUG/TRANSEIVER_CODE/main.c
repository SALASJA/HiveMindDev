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
uint8_t rx_address[5] = {'?','?','?','?','?'};
uint8_t tx_address[5] = {'!','!','!','!','!'};
uint8_t success_mode = FALSE;         //I feel success mode should automatically be off
char success[32] = "<<<success>>>";//13
char prev_data[32];


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
			//nrf24_getData(receive_buffer);
			printf("RECEIVED\n");
		}

		_delay_ms(10);
    }
}



