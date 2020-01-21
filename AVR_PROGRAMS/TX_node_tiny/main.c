#include <stdio.h>
#include <avr/io.h>
#include <stdint.h>
#include "../NRF24L01/nrf24.h"
#include <util/delay.h>


void copy(char * string, uint8_t * data_array);

int main()
{

	uint8_t temp;
	uint8_t q = 0;
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
	uint8_t c = 65;
	for(int i = 0; i < 26; i++){
		data_array[i] = 65 + i;
	}
	data_array[27] = 0;
	data_array[26] = c;
	
    while(1)
    {                
        /* Fill the data buffer */
        

        /* Automatically goes to TX mode */

        nrf24_send(data_array);        
        
        /* Wait for transmission to end */
        while(nrf24_isSending());

        /* Make analysis on last tranmission attempt */
        temp = nrf24_lastMessageStatus();


        
		/* Retranmission count indicates the tranmission quality */
		temp = nrf24_retransmissionCount();
		

		/* Optionally, go back to RX mode ... */
		nrf24_powerUpRx();

		/* Or you might want to power down after TX */
		// nrf24_powerDown();            

		/* Wait a little ... */
		_delay_ms(150);
		c++;
		if (c == (65 + 26))
			c = 65;
		data_array[26] = c;
    }
}


