#ifndef NODE_PROPERTIES_H
#define NODE_PROPERTIES_H

#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <util/delay.h>
#include "NRF24L01/nrf24.h"
#include "UART/uart.h"
#include "node_properties.h"

#define TRUE 1
#define FALSE 0
#define NOOP (void)0
static uint8_t receive_buffer[32];
static uint8_t data_buffer[32];
static uint8_t data_buffer_index = 0;
static uint8_t receiving = FALSE;
static uint8_t success_mode = FALSE;
static uint8_t TX_ADDR_VAL[5] = {'?','?','?','?','?'};
static uint8_t RX_ADDR_P_VAL[6][5] = {{'?','?','?','?','?'},
							   {'!','!','!','!','1'},
							   {'!','!','!','!','2'},
							   {'!','!','!','!','3'},
							   {'!','!','!','!','4'},
							   {'!','!','!','!','5'}};

#define toggle_success_mode(x) x = !x
void left_shift(uint8_t * data_buffer);
uint8_t is_success(uint8_t * recieve, uint8_t * success);
uint8_t print_address(uint8_t * address);
void setAddress(uint8_t * address_buffer, uint8_t * new_address, uint8_t mode, uint8_t pipe);
void process_uart_input();
void process_recieved(); 
#endif