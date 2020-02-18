#ifndef NODE_PROPERTIES_H
#define NODE_PROPERTIES_H

#include <avr/io.h>
#include "UART/uart.h"
#include "NRF24L01/nrf24.h"

#define TRUE 1
#define FALSE 0
#define toggle_success_mode(x) x = !x
void left_shift(uint8_t * data_buffer);
uint8_t is_success(uint8_t * recieve, uint8_t * success);
uint8_t print_address(uint8_t * address);
void setAddress(uint8_t * address_buffer, uint8_t * new_address, uint8_t mode, uint8_t pipe);
void process_uart_input(uint8_t * data_buffer, uint8_t * tx_address, uint8_t rx_address[][5], uint8_t * success_mode);
void process_recieved(uint8_t * recieve_buffer, uint8_t * tx_address, uint8_t rx_address[][5], uint8_t * success_mode, uint8_t * receiving); 

#endif