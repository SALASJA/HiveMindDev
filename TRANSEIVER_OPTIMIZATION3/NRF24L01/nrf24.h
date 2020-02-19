#ifndef NRF24_H
#define NRF24_H


extern "C"{
#include "../SPI/spi.h"
#include "nRF24L01.h"
#include <stdint.h>
}
#include util.h



class Nrf24{
	public:
		uint8_t receiving = FALSE;
		uint8_t success_mode = TRUE; //not a property of the transceiver though I should just extend the class 
		uint8_t payload_len = 32;
		uint8_t nrf24_ADDR_LEN  = 5;
		uint8_t NRF24_TRANSMISSON_OK  = 0;
		uint8_t NRF24_MESSAGE_LOST  = 1;
		uint8_t nrf24_CONFIG  = (1<<EN_CRC)|(0<<CRCO);
		uint8_t TX_ADDR_VAL[5] = {'1','!','!','!','!'};
		uint8_t RX_ADDR_P_VAL[6][5] = {{'1','!','!','!','!'}, //it has to be backwards
                              		   {'6','!','!','!','!'},
                               		   {'7','!','!','!','!'},
                                       {'8','!','!','!','!'},
                                       {'9','!','!','!','!'},
                                       {'A','!','!','!','!'}};
		/* adjustment functions */
		Nrf24();
		
		void init();
		
		void standardConfig();
		
		void set_RX_address(uint8_t * adr, uint8_t pipe);
		uint8_t * get_RX_address();
		
		void set_TX_address(uint8_t * adr);
		uint8_t * get_TX_address();
		
		void set_CONFIG_Register(uint8_t value);
		uint8_t get_CONFIG_Register();
		
		void set_EN_AA_Register(uint8_t * adr);
		uint8_t get_EN_AA_Register();
		
		void set_EN_RXADDR_Register(uint8_t value);
		uint8_t get_EN_RXADDR_Register();
		
		void set_SETUP_AW_Register(uint8_t value);
		uint8_t get_SETUP_AW_Register();
		
		void set_SETUP_RETR_Register(uint8_t value);
		uint8_t get_SETUP_RETR_Register();
		
		void set_RF_CH_Register(uint8_t value);
		uint8_t get_RF_CH_Register();
		
		void set_RF_SETUP_Register(uint8_t value);
		uint8_t get_RF_SETUP_Register();
		
		void set_STATUS_Register(uint8_t value);
		uint8_t get_STATUS_Register();
		
		void set_OBSERVE_TX_Register(uint8_t value);
		uint8_t get_OBSERVE_TX_Register();
		
		void set_RX_PW_PN_Register(uint8_t value, uint8_t pipe);
		uint8_t get_RX_PW_PN_Register(uint8_t pipe);
		
		
		
		
		
		
		
		uint8_t isReceiving();
		
		uint8_t isSuccessMode();
		void setSuccessMode(uint8_t value);

		/* state check functions */
		uint8_t dataReady();
		
		uint8_t rxFifoEmpty();
		
		uint8_t isSending();

		uint8_t getStatus();
		
		/* core TX / RX functions */
		void send(uint8_t* value);
		
		void getData(uint8_t* data);


		/* post transmission analysis */
		uint8_t lastMessageStatus();
		
		uint8_t retransmissionCount();
		/* Returns the payload length */
		uint8_t payloadLength();

		/* power management */
		void powerUpRx();
		
		void powerUpTx();

		void powerDown();

		/* low level interface ... */
		void transferSync(uint8_t* dataout,uint8_t* datain,uint8_t len);

		/* send multiple bytes over SPI */
		void transmitSync(uint8_t* dataout,uint8_t len);
		
		/* Clocks only one byte into the given nrf24 register */
		void configRegister(uint8_t reg, uint8_t value);

		/* Read single register from nrf24 */
		void readRegister(uint8_t reg, uint8_t* value, uint8_t len);

		/* Write to a single register of nrf24 */
		void writeRegister(uint8_t reg, uint8_t* value, uint8_t len);
};

#endif