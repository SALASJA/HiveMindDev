#ifndef SPI_H
#define SPI_H

#include <avr/io.h>


//this is a software based, so different pins can be used
//change these macros to reflect what pins you want and need to use, very portable if working with
//these are macros, defining arguments, its weird but it works 
#define HIGH 1
#define LOW 0

#define CE_Pin DDRB,2
#define CSN_Pin DDRB,1
#define SCK_Pin DDRB,5
#define MOSI_Pin DDRB,3
#define MISO_Pin DDRB,4

#define set_bit(reg,bit) reg |= (1<<bit)
#define clr_bit(reg,bit) reg &= ~(1<<bit)
#define check_bit(reg,bit) (reg & (1<<bit))
#define getBitL(byte,position) byte & ( 1 << (7 - position))
#define getBitR(byte,position) byte & ( 1 << position)

#define set_HIGH(reg,bit) set_bit(reg,bit)
#define set_LOW(reg,bit) clr_bit(reg,bit)
#define get_Pin_State(reg,bit) check_bit(reg,bit)					  

//redundant macros help to improve clarity of code
#define set_CE_HIGH() set_HIGH(CE_Pin)
#define set_CE_LOW() set_LOW(CE_Pin)

#define set_CSN_HIGH() set_HIGH(CSN_Pin)
#define set_CSN_LOW() set_LOW(CSN_Pin)

#define set_SCK_HIGH() set_HIGH(SCK_Pin)
#define set_SCK_LOW() set_LOW(SCK_Pin)

#define set_MOSI_HIGH() set_HIGH(MOSI_Pin)
#define set_MOSI_LOW() set_LOW(MOSI_Pin)
#define get_MOSI_State() get_Pin_State(MOSI_Pin)

#define set_MISO_HIGH() set_HIGH(MISO_Pin)
#define set_MISO_LOW() set_LOW(MISO_Pin)
#define get_MISO_State() get_Pin_State(MISO_Pin)


// MISO input   will change to pin 12    PB4
// MOSI output  will change to pin 11    PB3
// SCK output   will change to pin 13 on PB5atmega328p
// CSN output   will change to pin 10    PB2
// CE output    will change to pin 9     PB1            
#define standardSPIPinInit() {
								    set_CE_HIGH(); \
    								set_CSN_HIGH(); \
    								set_SCK_HIGH(); \
   			 						set_MOSI_HIGH(); \
    								set_MISO_LOW(); \
							 }
							 
#define writeBit(bit) {
						if(bit){             \
							set_MOSI_HIGH(); \           
						}                    \
						else{                \
							set_MOSI_LOW();  \
						}                    \
					  }

#define receiveBit(bits_received) {
									bits_received = bits_received << 1; \
									if(get_MISO_State()){ \
										bits_received |= 0x01; \
									} \
					 			  }



uint8_t spi_transfer(uint8_t byte_to_send);


#endif