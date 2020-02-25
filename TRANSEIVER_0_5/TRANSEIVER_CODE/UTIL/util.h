#ifndef UTIL_H
#define UTIL_H
#include <avr/io.h>
#include "../NRF24L01/nrf24.h"
extern "C"{
#include "../UART/uart.h"
}
#define TRUE 1
#define FALSE 0

void printRegisters(Nrf24 &transeiver);
void copy(uint8_t * buffer_1, uint8_t * buffer_2);
uint8_t is_success(uint8_t * recieve, uint8_t * success);
void print_address(uint8_t * address);
void print_RX_address(Nrf24 &transeiver, uint8_t pipe);
void print_TX_address(Nrf24 &transeiver);
void print_receive(uint8_t * buffer);
void print_success(uint8_t * buffer);
void process_uart_input(Nrf24 &transeiver, uint8_t * data_buffer);
void process_recieved(Nrf24 &transeiver, uint8_t * recieve_buffer); 

#endif
