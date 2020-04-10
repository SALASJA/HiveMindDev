#ifndef SPI_H
#define SPI_H

#include <avr/io.h>
#include <stdint.h>


//this is a software based, so different pins can be used
//change these macros to reflect what pins you want and need to use, very portable if working with
//these are macros, defining arguments, its weird but it works 
#define HIGH 1
#define LOW 0

#define set_bit(reg,bit) reg |= (1<<bit)
#define clr_bit(reg,bit) reg &= ~(1<<bit)
#define check_bit(reg,bit) (reg & (1<<bit))
#define getBitL(byte,position) byte & ( 1 << (7 - position))
#define getBitR(byte,position) byte & ( 1 << position)

#define set_HIGH(reg,bit) set_bit(reg,bit)
#define set_LOW(reg,bit) clr_bit(reg,bit)
#define get_Pin_State(reg,bit) check_bit(reg,bit)					  

#define set_CE_Pin(reg, bit) set_HIGH(reg,bit)
#define set_CSN_Pin(reg, bit) set_HIGH(reg,bit)
#define set_SCK_Pin(reg, bit) set_HIGH(reg,bit)
#define set_MOSI_Pin(reg, bit) set_HIGH(reg,bit)
#define set_MISO_Pin(reg, bit) clr_bit(reg,bit)

#define DataDirectionRegister DDRB
#define PinOnOffRegister PORTB
#define PinStateRegister PINB

#define SCK_Pin 5
#define MISO_Pin 4
#define MOSI_Pin 3
#define CE_Pin 2
#define CSN_Pin 1

// SCK output   will change to pin 13 on PB5atmega328p
// MISO input   will change to pin 12    PB4
// MOSI output  will change to pin 11    PB3
// CE output    will change to pin 10     PB1    

// CSN output   will change to pin 9    PB2    


void standardSPIPinInit();

void set_CE(uint8_t state);

void set_CSN(uint8_t state);

void set_SCK(uint8_t state);

void set_MOSI(uint8_t state);
            
uint8_t get_MISO_State();

uint8_t spi_transfer(uint8_t byte_to_send);


#endif