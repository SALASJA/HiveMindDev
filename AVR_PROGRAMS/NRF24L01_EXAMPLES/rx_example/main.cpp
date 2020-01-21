/*
* ----------------------------------------------------------------------------
* “THE COFFEEWARE LICENSE” (Revision 1):
* <ihsan@kehribar.me> wrote this file. As long as you retain this notice you
* can do whatever you want with this stuff. If we meet some day, and you think
* this stuff is worth it, you can buy me a coffee in return.
* -----------------------------------------------------------------------------
*/

#include <avr/io.h>
#include <stdint.h>
#include "../nrf24.h"
#include <util/delay.h>
#include "../Framebuffer.h"

#define set_bit(reg,bit) reg |= (1<<bit)
#define clr_bit(reg,bit) reg &= ~(1<<bit)
#define check_bit(reg,bit) (reg&(1<<bit))

void nrf24_setupPins();

uint8_t data_array[4];
uint8_t tx_address[5] = {0xD7,0xD7,0xD7,0xD7,0xD7};
uint8_t rx_address[5] = {0xE7,0xE7,0xE7,0xE7,0xE7};

int main(){
	Framebuffer fb;
	
    /* init hardware pins */
    nrf24_init();
    
    /* Channel #2 , payload length: 4 */
    nrf24_config(2,4);                     //working starting channel was     nrf24_config(2,4) 
 
    /* Set the device addresses */
    nrf24_tx_address(tx_address);
    nrf24_rx_address(rx_address);

    while(1)
    {    
        if(nrf24_dataReady())
        {	fb.clear();
            nrf24_getData(data_array);
            fb.drawPixel(data_array[0], data_array[1]);
            fb.show();        

        }
    }
}


/* ------------------------------------------------------------------------- */

