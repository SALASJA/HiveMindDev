/**
 * attiny85 pin map:
 *                              +-\/-+
 *                NC      PB5  1|o   |8  Vcc --- nRF24L01  3v3, pin2
 * nRF24L01  CE, pin3 --- PB3  2|    |7  PB2 --- nRF24L01  SCK, pin5
 * nRF24L01 CSN, pin4 --- PB4  3|    |6  PB1 --- nRF24L01 MOSI, pin6
 * nRF24L01 GND, pin1 --- GND  4|    |5  PB0 --- nRF24L01 MISO, pin7
 *                              +----+
 */

/**
 * Device settings
 */
#define CHANNEL 0x01 //0x4c
#define P0_ADDR 0xD7 //0xE7
#define CID 0xC2
#define PAYLOAD_WIDTH 32 //1

#define F_CPU 1000000UL

#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>
#include "nRF24L01.h"

/**
 * Simavr debugging
 */


/**
 * Simple macros for setting/clearing bits
 */
#define BIT(x) (_BV(x))
#define SETBITS(x,y) ((x) |= (y))
#define CLEARBITS(x,y) ((x) &= (~(y)))
#define SETHIGH(x,y) SETBITS((x), (BIT((y))))
#define SETLOW(x,y) CLEARBITS((x), (BIT((y))))

#define CSN PB4
#define CE PB3



/**
 * nRF Config
 */
void init_spi(void) {
    // Set PB2 (SCK), PB1 (MISO/NRF_MOSI), PB4 (CSN), and PB3 (CE) as output
    // Has to be set before SPI-Enable below
    DDRB |= _BV(PB2) | _BV(PB1) | _BV(PB4) | _BV(PB3);

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
/*
uint8_t write_byte_spi(uint8_t c_data) {
    // Load byte to Data register
    USIDR = c_data;

    // clear flag to be able to receive new data
    USISR |= _BV(USIOIF);

    // Wait for transmission to complete 
    while ((USISR & _BV(USIOIF)) == 0) {
        // Toggle SCK and count a 4-bit counter from 0-15,
        // When it reaches 15 USIOIF is set!
        USICR |= _BV(USITC);
    }

    _delay_us(10);

    return USIDR;
}*/

uint8_t write_byte_spi(uint8_t _data) {
  USIDR = _data;
  USISR = _BV(USIOIF);
  
  while((USISR & _BV(USIOIF)) == 0){
    USICR = _BV(USIWM0) | _BV(USICS1) | _BV(USICLK) | _BV(USITC);
  }
  return USIDR;
}

uint8_t get_reg(uint8_t reg) {
    _delay_us(10);
    // CSN low - nRF starts to listen for command
    SETLOW(PORTB, CSN);
    _delay_us(10);
    // R_Register = set the nRF to reading mode, "reg" = this registry will be read back
    write_byte_spi(R_REGISTER + reg);

    // Send NOP (dummy byte) once to receive back the first byte in the "reg" register
    reg = write_byte_spi(NOP);

    // CSN Hi - nRF goes back to doing nothing
    SETHIGH(PORTB, CSN);

    return reg;
}

uint8_t *nrf_read(uint8_t reg, uint8_t bytes) {
    static uint8_t ret[32];
    if (reg == W_TX_PAYLOAD) {
        // W_TX_PAYLOAD is invalid for reading.
        return ret;
    }

    // CSN low - nRF starts to listen for command
    SETLOW(PORTB, CSN);
    _delay_us(10);

    // tell the nRF which register we're working with
    write_byte_spi(reg);

    // Send dummy bytes to read out the data
    int i;
    for (i=0; i<bytes; i++) {
        ret[i] = write_byte_spi(NOP);
    }

    // CSN High - nRF goes back to doing nothing
    SETHIGH(PORTB, CSN);

    return ret;
}

void nrf_write_bytes(uint8_t reg, uint8_t *bytes, uint8_t size) {
    // Add the "write" bit to the "reg"
    if (reg != W_TX_PAYLOAD) {
        reg = W_REGISTER + reg;
    }

    // CSN low - nRF starts to listen for command
    SETLOW(PORTB, CSN);
    _delay_us(10);

    // tell the nRF which register we're working with
    write_byte_spi(reg);

    int i;
    for (i=0; i<size; i++) {
        write_byte_spi(bytes[i]);
    }

    // CSN High - nRF goes back to doing nothing
    SETHIGH(PORTB, CSN);
    _delay_us(10);
}

void nrf_write(uint8_t reg, uint8_t value) {
    uint8_t bytes[] = {value};
    nrf_write_bytes(reg, bytes, 1);
}


void nrf24L01_init(void) {
    // allow radio to reach power down if shut down
    _delay_ms(100);

    // Enable auto-ack on P0
    nrf_write(EN_AA, 0x01);

    // Set the number of retries and delay
    // 0xFF = 1111 1111: 4000ms delay, 15 retransmit count
    nrf_write(SETUP_RETR, 0xFF);

    // Choose the number of enabled data pipes (1-5)
    nrf_write(EN_RXADDR, 0x01);

    // RF_Address width setup (how many bytes is the receiver address, the more the merrier 1-5)
    // 0x03 = 0000 0011: 5 bytes RF_Address
    nrf_write(SETUP_AW, 0x03);

    // RF channel setup - choose frequency 2,400-2,575GHz 1MHz/step
    nrf_write(RF_CH, CHANNEL);

    // RF setup - choose power mode and data speed.
    // 0x26 = 0010 0111: 250kbps, High power
    nrf_write(RF_SETUP, 0x26);

    // Set RX address
    uint8_t rx_addr[5];
    int i;
    for (i=0; i<5; i++) {
        rx_addr[i] = P0_ADDR;
    }
    nrf_write_bytes(RX_ADDR_P0, rx_addr, 5);

    // Set our static payload width
    nrf_write(RX_PW_P0, PAYLOAD_WIDTH);

    /*
    Write the CONFIG register (0x1E = 00011110)
    bit 0="0": Act as transmitter
    bit 1="1": power up
    bit 2="1": set CRC to 2-byte
    bit 3="1": enable CRC
    bit 4="1": MASK_MAX_RT (IRQ not triggered if transmission failed)
    */
    nrf_write(CONFIG, 0x1A)//0x1E); 0001 1110

    // device need 1.5ms to reach standby mode (CE=low)
    _delay_ms(100);
}

void transmit_payload(uint8_t *payload, uint8_t size) {
    // Send FLUSH_TX to flush the registry from old data,
    nrf_read(FLUSH_TX, 0);

    // Send the data in payload to the nrf.
    /*uint8_t payload2[size];
    int i;
    for (i=0; i < size; i++) {
        payload2[i] = payload[i];
    }*/
    nrf_write_bytes(W_TX_PAYLOAD, payload, size);

    // sei(); // Enable global interrupt (if interrupt is used)

    // needs a 10ms delay to work after loading the nrf with the payload for some reason
    _delay_ms(10);

    // CE high = transmit the data!
    SETHIGH(PORTB, CE);
    _delay_us(20);

    // CE low = stop transmitting
    SETLOW(PORTB, CE);
    _delay_ms(10);

    /*
    if ((get_reg(STATUS) & _BV(4)) != 0) {
        // transmission failed;
    }
    */
}

void reset(void) {
    _delay_us(10);

    // CSN low
    SETLOW(PORTB, 2);
    _delay_us(10);

    // Write to STATUS registry
    write_byte_spi(W_REGISTER + STATUS);

    // Reset all IRQ in STATUS registry
    write_byte_spi(0x70);

    // CSN IR_High
    SETHIGH(PORTB, 2);
}

int main(void) {
    init_spi();
    nrf24L01_init();

    // Send 1, 2, 3, 4, 5 every second
    int i;
    uint8_t payload[32];
    for (i=0; i<30; i++) {
        payload[i] = (i + 65) % 26 + 65;
    }
    payload[30] = 0;
    
    transmit_payload(payload, sizeof payload / sizeof *payload);
    _delay_us(1);
    reset();
    sleep_cpu();
    return 0;
}