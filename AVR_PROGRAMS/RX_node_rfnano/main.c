#include <stdlib.h>
#include <avr/io.h>
#include <stdint.h>
#include "../NRF24L01/nrf24.h"
#include <util/delay.h>
#include "../SSD1306_C/Files/SSD1306.h"
#include "../SSD1306_C/Files/Font5x8.h"

#define set_bit(reg,bit) reg |= (1<<bit)
#define clr_bit(reg,bit) reg &= ~(1<<bit)
#define check_bit(reg,bit) (reg&(1<<bit))

void nrf24_setupPins();
void copy(uint8_t * data_array, char * string);

int main(){
	GLCD_Setup();
	GLCD_SetFont(Font5x8, 5, 8, GLCD_Overwrite);

	GLCD_GotoXY(0, 0);
	uint8_t data_array[32];
	char * string = (char *)malloc(32);
	uint8_t tx_address[5] = {0xD7,0xD7,0xD7,0xD7,0xD7};
	uint8_t rx_address[5] = {0xE7,0xE7,0xE7,0xE7,0xE7};
	
    /* init hardware pins */
    nrf24_init();
    
    /* Channel #2 , payload length: 4 */
    nrf24_config(2,32);                     //working starting channel was     nrf24_config(2,4) before was 32 bits
 
    /* Set the device addresses */
    nrf24_tx_address(tx_address);
    nrf24_rx_address(rx_address);

    while(1)
    {    
        if(nrf24_dataReady())
        {	
        	
            nrf24_getData(data_array);
            GLCD_Clear();
            copy(data_array, string);
        	drawText(string, 0,0);
        	//GLCD_SetPixel(0,data_array[0], GLCD_Black);
        	GLCD_Render();
        	_delay_ms(100);

        }
    }
}

void copy(uint8_t * data_array, char * string){
	uint8_t i = 0;
	while(data_array[i] != 0){
		string[i] = data_array[i];
		i++;
	}
	string[i] = data_array[i];
	
}