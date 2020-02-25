#include "node_properties.h"

//try just setting up for multiple nodes first 
extern uint8_t receive_buffer[32];
extern uint8_t data_buffer[32];
static uint8_t data_buffer_index = 0;
static uint8_t receiving = FALSE;
static uint8_t success_mode = FALSE;
void main(){
	USART_Init();
	nrf24_init();
	sei();
	nrf24_config2();
	DDRD |= (1 << 5); //can comment out these lines but can now give us insight on external controll
    while(1)
    {                
		/* Optionally, go back to RX mode ... */
		if(!receiving){
			nrf24_powerUpRx();
			receiving = TRUE;
		}
		if(nrf24_dataReady()){
			nrf24_getData(receive_buffer);
			process_recieved();
        }
		_delay_ms(10);
    }
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
		process_uart_input();
		receiving = FALSE; 
	}
	sei();
}

