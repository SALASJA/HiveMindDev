#include <avr/io.h>

#define set_bit(reg,bit) reg |= (1<<bit)
#define clr_bit(reg,bit) reg &= ~(1<<bit)
#define check_bit(reg,bit) (reg&(1<<bit))

#define SCK PB2
#define MOSI PB1
#define CSN PB4
#define CE PB3
#define MISO PB0

void nrf24_setupPins(){
    set_bit(DDRB,CE); // CE output    will change to pin 9     PB1            
    set_bit(DDRB,CSN); // CSN output   will change to pin 10    PB2
    set_bit(DDRB,SCK); // SCK output   will change to pin 13 on atmega328p   PB5
    set_bit(DDRB,MOSI); // MOSI output  will change to pin 11    PB3
    clr_bit(DDRB,MISO); // MISO input   will change to pin 12    PB4
}

/*
void nrf24_setupPins() {
    // Set PB2 (SCK), PB1 (MISO/NRF_MOSI), PB4 (CSN), and PB3 (CE) as output
    // Has to be set before SPI-Enable below
    DDRB |= _BV(SCK) | _BV(MOSI) | _BV(CSN) | _BV(CE);

    // Set PB0 (MOSI/NRF_MISO) as input, and set it low
    DDRB &= ~_BV(PB0);
    PORTB |= _BV(PB0);

    // Configure USI (Universal Serial Interface)
    // Wire Mode 0,1: Three-wire mode (uses DO, DI, & USCK pins)
    // Clock Source Select 1,0,1: Ext. positive edge, software clock strobe
    USICR |= _BV(USIWM0) | _BV(USICS1) | _BV(USICLK) | _BV(USITC);

    // PB4 (CSN) high to start with, nothing to be sent to the nRF yet!
    SETHIGH(PORTB, CSN);

    // PB3 (CE) low to start with, nothing to send/receive yet!
    SETLOW(PORTB, CE);
}
*/

void nrf24_ce_digitalWrite(uint8_t state)
{
    if(state)
    {
        set_bit(PORTB,CE);
    }
    else
    {
        clr_bit(PORTB,CE);
    }
}

void nrf24_csn_digitalWrite(uint8_t state)
{
    if(state)
    {
        set_bit(PORTB,CSN);
    }
    else
    {
        clr_bit(PORTB,CSN);
    }
}

void nrf24_sck_digitalWrite(uint8_t state)
{
    if(state)
    {
        set_bit(PORTB,SCK);
    }
    else
    {
        clr_bit(PORTB,SCK);
    }
}

void nrf24_mosi_digitalWrite(uint8_t state)
{
    if(state)
    {
        set_bit(PORTB,MOSI);
    }
    else
    {
        clr_bit(PORTB,MOSI);
    }
}

uint8_t nrf24_miso_digitalRead()
{
    return check_bit(PINB,MISO);
}
