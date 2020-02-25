#include <util/delay.h>
#include <avr/interrupt.h>
#include "NRF24L01/nrf24.h"
extern "C"{
#include "UART/uart.h"
}
#include "UTIL/util.h"



Nrf24 transeiver;
uint8_t data_buffer[32];
uint8_t receive_buffer[32];
uint8_t data_buffer_index = 0;

int main(){
	USART_Init();
	transeiver.init();
	transeiver.standardConfig();
	transeiver.powerUpRx();
	sei();
	while(TRUE){
		/* Optionally, go back to RX mode ... */
		if(!transeiver.isReceiving()){
			transeiver.powerUpRx();
		}
		if(transeiver.dataReady()){
			transeiver.getData(receive_buffer);
			process_recieved(transeiver, receive_buffer);
        }
		/* Or you might want to power down after TX */
		// nrf24_powerDown();            
		/* Wait a little ... */
		_delay_ms(10);
	}
	return 0;
}

ISR(USART_RX_vect) //its a lot like a GUI event if you have worked with those, maybe i need to add the backspace feature for those who dont want a gui
{	
	uint8_t receivedByte;
	receivedByte = (uint8_t) USART_Receive(); // Fetch the received byte value into the variable "ByteReceived"
	data_buffer[data_buffer_index] = receivedByte;
	data_buffer_index++;
	if(data_buffer_index == 31 || receivedByte == '\r'){
		data_buffer[data_buffer_index] = 0;
		data_buffer_index = 0;
		process_uart_input(transeiver, data_buffer);

	}
	sei();
}