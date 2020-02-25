/*
	HIVEMIND Project edits
 */
 
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <util/delay.h>
#include "NRF24L01/nrf24.h"
#include "UART/uart.h"
#include "node_properties.h"

uint8_t receive_buffer[32];
uint8_t data_buffer[32];
uint8_t data_buffer_index = 0;
uint8_t receiving = FALSE;
uint8_t TX_ADDR_VAL[5] = {'1','!','!','!','!'};
uint8_t RX_ADDR_P_VAL[6][5] = {{'1','!','!','!','!'}, //it has to be backwards
                               {'6','!','!','!','!'},
                               {'7','!','!','!','!'},
                               {'8','!','!','!','!'},
                               {'9','!','!','!','!'},
                               {'A','!','!','!','!'}};
uint8_t success_mode = FALSE;         //I feel success mode should automatically be off
//char success[32] = "<<<success>>>";//13 characters
//should there be a constant sending mode?
int main()
{
	USART_Init();
    nrf24_init();
    
    /* Channel #2 , payload length: 4 */
    nrf24_config2();

    /* Set the device addresses */
    nrf24_tx_address(TX_ADDR_VAL);
    for(int i = 1; i <= 5; i++){
    	nrf24_rx_address(RX_ADDR_P_VAL[i], i);  //address get fed backwards when communucated to nrf24l01
    }
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
			process_recieved(receive_buffer, TX_ADDR_VAL, RX_ADDR_P_VAL, &success_mode, &receiving);
        }
		/* Or you might want to power down after TX */
		// nrf24_powerDown();            
		/* Wait a little ... */
		_delay_ms(10);
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
		process_uart_input(data_buffer, TX_ADDR_VAL, RX_ADDR_P_VAL, &success_mode);
		receiving = FALSE; 

	}
	sei();
}

