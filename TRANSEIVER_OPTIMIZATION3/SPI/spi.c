#include "spi.h"

uint8_t spi_transfer(uint8_t byte_to_send)
{
    uint8_t i = 0;
    uint8_t bits_received = 0;    
    set_SCK_LOW();
    for(i = 0; i < 8; i++){
		
        writeBit(getBitL(byte_to_send, i)); // writes Bit to mosi by either setting it high or low


        set_SCK_HIGH();        

		receiveBit(bits_received); //gets bit from miso by checking if its high and pushes it onto byte sized variable from right

        set_SCK_LOW();               

    }

    return bits_received;
}