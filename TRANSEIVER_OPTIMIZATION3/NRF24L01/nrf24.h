#ifndef NRF24_H
#define NRF24_H

#ifdef __cplusplus
extern "C"{
#endif

#include "nRF24L01.h"
#include "../SPI/spi.h"
#include <stdint.h>

#ifdef __cplusplus
}
#endif


#define NRF24_TRANSMISSON_OK 0
#define NRF24_MESSAGE_LOST   1

class Nrf24{
	public:
		uint8_t payload_len = 32;
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
		
		void set_RX_address(uint8_t * adr, uint8_t pipe);
		
		void set_TX_address(uint8_t* adr);

		/* state check functions */
		uint8_t dataReady();
		
		uint8_t rxFifoEmpty();
		
		uint8_t isSending();

		uint8_t getStatus();
		
		/* core TX / RX functions */
		void send(uint8_t* value);
		
		void getData(uint8_t* data);

		/* use in dynamic length mode */
		uint8_t payloadLength();

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