/*
	HIVEMIND Project edits
 */
 
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <util/delay.h>
#include "NRF24L01/nrf24.h"
#include "UART/uart.h"
#include "node_properties.h"

uint8_t receive_buffer[32];
uint8_t data_buffer[32];
uint8_t data_buffer_index = 0;
uint8_t receiving = FALSE;
uint8_t TX_ADDR_VAL[5] = {'?','?','?','?','?'};
uint8_t RX_ADDR_P_VAL[6][5] = {{'?','?','?','?','?'},
                               {'!','!','!','!','1'},
                               {'!','!','!','!','2'},
                               {'!','!','!','!','3'},
                               {'!','!','!','!','4'},
                               {'!','!','!','!','5'}};
uint8_t success_mode = FALSE;         //I feel success mode should automatically be off
//char success[32] = "<<<success>>>";//13 characters
//should there be a constant sending mode?
int main()
{
	USART_Init();
    nrf24_init();
    
    /* Channel #2 , payload length: 4 */
    nrf24_config2();

    /* Set the device addresses */
    nrf24_tx_address(TX_ADDR_VAL);
    for(int i = 1; i <= 5; i++){
    	nrf24_rx_address(RX_ADDR_P_VAL[i], i);
    }
    
    while(1){
		uint8_t reg = 0;
		nrf24_readRegister(CONFIG, &reg, 1);
		printf(":CONFIG: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(EN_AA, &reg, 1);
		printf(":EN_AA: %x\n", reg);

		reg = 0;
		nrf24_readRegister(EN_RXADDR, &reg, 1);
		printf(":EN_RXADDR: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(SETUP_AW, &reg, 1);
		printf(":SETUP_AW: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(SETUP_RETR, &reg, 1);
		printf(":SETUP_RETR: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(RF_CH, &reg, 1);
		printf(":RF_CH: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(RF_SETUP, &reg, 1);
		printf(":RF_SETUP: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(STATUS, &reg, 1);
		printf(":STATUS: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(OBSERVE_TX, &reg, 1);
		printf(":OBSERVE_TX: %x\n", reg);
	
		//reg = 0;
		//nrf24_readRegister(RPD, &reg, 1);
		//printf("RPD: %x\n", reg);
	
		uint8_t reg_vals[6] = {0,0,0,0,0,0};
		nrf24_readRegister(RX_ADDR_P0, reg_vals, 5);
		printf(":RX_ADDR_P0: %s\n", reg_vals);
	
		nrf24_readRegister(RX_ADDR_P1, reg_vals, 5);
		printf(":RX_ADDR_P1: %s\n", reg_vals);
	
		reg = 0;
		nrf24_readRegister(RX_ADDR_P2, &reg, 1);
		printf(":RX_ADDR_P2: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(RX_ADDR_P3, &reg, 1);
		printf(":RX_ADDR_P3: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(RX_ADDR_P4, &reg, 1);
		printf(":RX_ADDR_P4: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(RX_ADDR_P5, &reg, 1);
		printf(":RX_ADDR_P5: %x\n", reg);
	
		nrf24_readRegister(TX_ADDR, reg_vals, 5);
		printf(":TX_ADDR: %s\n", reg_vals);
	
		reg = 0;
		nrf24_readRegister(RX_PW_P0, &reg, 1);
		printf(":RX_PW_P0: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(RX_PW_P1, &reg, 1);
		printf(":RX_PW_P1: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(RX_PW_P2, &reg, 1);
		printf(":RX_PW_P2: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(RX_PW_P3, &reg, 1);
		printf(":RX_PW_P3: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(RX_PW_P4, &reg, 1);
		printf(":RX_PW_P4: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(RX_PW_P5, &reg, 1);
		printf(":RX_PW_P5: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(FIFO_STATUS, &reg, 1);
		printf(":FIFO_STATUS: %x\n", reg);
	
		reg = 0;
		nrf24_readRegister(DYNPD, &reg, 1);
		printf(":DYNPD: %x\n", reg);
	
		//reg = 0;
		//nrf24_readRegister(FEATURE, &reg, 1);
		//printf("FEATURE: %x\n", reg);
	}
	
    
    
    
    
    
     
    /*
    sei();    
	DDRD |= (1 << 5); //can comment out these lines but can now give us insight on external controll
    while(1)
    {                
		//Optionally, go back to RX mode ... 
		if(!receiving){
			nrf24_powerUpRx();
			receiving = TRUE;
		}
		if(nrf24_dataReady()){
			nrf24_getData(receive_buffer);
			process_recieved(receive_buffer, TX_ADDR_VAL, RX_ADDR_P_VAL, &success_mode, &receiving);
        }
		// Or you might want to power down after TX 
		// nrf24_powerDown();            
		//Wait a little ... 
		_delay_ms(10);
    }*/
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
		process_uart_input(data_buffer, TX_ADDR_VAL, RX_ADDR_P_VAL, &success_mode);
		receiving = FALSE; 

	}
	sei();
}

