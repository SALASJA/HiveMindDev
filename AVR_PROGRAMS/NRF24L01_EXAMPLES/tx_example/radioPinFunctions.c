#include <avr/io.h>

#define set_bit(reg,bit) reg |= (1<<bit)
#define clr_bit(reg,bit) reg &= ~(1<<bit)
#define check_bit(reg,bit) (reg&(1<<bit))

/* ------------------------------------------------------------------------- */
void nrf24_setupPins(){
    set_bit(DDRB,1); // CE output    will change to pin 9     PB1            
    set_bit(DDRB,2); // CSN output   will change to pin 10    PB2
    set_bit(DDRB,5); // SCK output   will change to pin 13 on atmega328p   PB5
    set_bit(DDRB,3); // MOSI output  will change to pin 11    PB3
    clr_bit(DDRB,4); // MISO input   will change to pin 12    PB4
}
/* ------------------------------------------------------------------------- */
void nrf24_ce_digitalWrite(uint8_t state)
{
    if(state)
    {
        set_bit(PORTB,1);
    }
    else
    {
        clr_bit(PORTB,1);
    }
}
/* ------------------------------------------------------------------------- */
void nrf24_csn_digitalWrite(uint8_t state)
{
    if(state)
    {
        set_bit(PORTB,2);
    }
    else
    {
        clr_bit(PORTB,2);
    }
}
/* ------------------------------------------------------------------------- */
void nrf24_sck_digitalWrite(uint8_t state)
{
    if(state)
    {
        set_bit(PORTB,5);
    }
    else
    {
        clr_bit(PORTB,5);
    }
}
/* ------------------------------------------------------------------------- */
void nrf24_mosi_digitalWrite(uint8_t state)
{
    if(state)
    {
        set_bit(PORTB,3);
    }
    else
    {
        clr_bit(PORTB,3);
    }
}
/* ------------------------------------------------------------------------- */
uint8_t nrf24_miso_digitalRead()
{
    return check_bit(PINB,4);
}
/* ------------------------------------------------------------------------- */

/* ------------------------------------------------------------------------- */
