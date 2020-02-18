/* adjustment functions */
#include "nrf24.h"

Nrf24::Nrf24(){
	
}

void Nrf24::init(){
		set_CE_LOW();
		set_CSN_HIGH();	
}

void Nrf24::set_RX_address(uint8_t * adr, uint8_t pipe){
	set_CE_LOW();
	switch(pipe){
		case 1:
				writeRegister(RX_ADDR_P1,adr,nrf24_ADDR_LEN);
				break;
		case 2: 
				writeRegister(RX_ADDR_P2,&adr[0],1); //pipes 2 to 5 have the least significant byte being different
				break;
		case 3: 
				writeRegister(RX_ADDR_P3,&adr[0],1);
				break; 
		case 4: 
				writeRegister(RX_ADDR_P4,&adr[0],1);
				break;
		case 5: 
				writeRegister(RX_ADDR_P5,&adr[0],1);
				break;
		default:
				break;
	} 

	set_CE_HIGH();

}

void Nrf24::set_TX_address(uint8_t* adr){
	/* RX_ADDR_P0 must be set to the sending addr for auto ack to work. */
	writeRegister(RX_ADDR_P0,adr,nrf24_ADDR_LEN); 
	writeRegister(TX_ADDR,adr,nrf24_ADDR_LEN);
}

/* state check functions */
uint8_t Nrf24::dataReady() {
	// See note in getData() function - just checking RX_DR isn't good enough
	uint8_t status = getStatus();

	// We can short circuit on RX_DR, but if it's not set, we still need
	// to check the FIFO for any pending packets
	if ( status & (1 << RX_DR) ) 
	{
		return 1;
	}

	return !rxFifoEmpty();;
}

uint8_t Nrf24::rxFifoEmpty(){
	uint8_t fifoStatus;

	readRegister(FIFO_STATUS,&fifoStatus,1);

	return (fifoStatus & (1 << RX_EMPTY));
}

uint8_t Nrf24::isSending()
{
	uint8_t status;

	/* read the current status */
	status = getStatus();
		
	/* if sending successful (TX_DS) or max retries exceded (MAX_RT). */
	if((status & ((1 << TX_DS)  | (1 << MAX_RT))))
	{        
		return 0; /* false */
	}

	return 1; /* true */

}

uint8_t Nrf24::getStatus()
{
	uint8_t rv;
	set_CSN_LOW();
	rv = spi_transfer(NOP);
	set_CSN_HIGH();
	return rv;
}


/* core TX / RX functions */
void Nrf24::send(uint8_t* value) {    
	/* Go to Standby-I first */
	set_CE_LOW();

	/* Set to transmitter mode , Power up if needed */
	powerUpTx();

	/* Do we really need to flush TX fifo each time ? */
	#if 1
		/* Pull down chip select */
		set_CSN_LOW()           

		/* Write cmd to flush transmit FIFO */
		spi_transfer(FLUSH_TX);     

		/* Pull up chip select */
		set_CSN_HIGH();                  
	#endif 

	/* Pull down chip select */
	set_CSN_LOW();

	/* Write cmd to write payload */
	spi_transfer(W_TX_PAYLOAD);

	/* Write payload */
	transmitSync(value,payload_len);   

	/* Pull up chip select */
	set_CSN_HIGH();

	/* Start the transmission */
	set_CE_HIGH();    
}


void Nrf24::getData(uint8_t* data) {
	/* Pull down chip select */
	set_CSN_LOW();                              

	/* Send cmd to read rx payload */
	spi_transfer( R_RX_PAYLOAD );

	/* Read payload */
	transferSync(data,data,payload_len);

	/* Pull up chip select */
	set_CSN_HIGH();

	/* Reset status register */
	configRegister(STATUS,(1<<RX_DR));   
}

/* use in dynamic length mode */
uint8_t Nrf24::payloadLength(){
	uint8_t status;
	set_CSN_LOW();
	spi_transfer(R_RX_PL_WID);
	status = spi_transfer(0x00);
	set_CSN_HIGH();
	return status;
}

/* post transmission analysis */
uint8_t Nrf24::lastMessageStatus()
{
	uint8_t rv;

	rv = getStatus();

	/* Transmission went OK */
	if((rv & ((1 << TX_DS))))
	{
		return NRF24_TRANSMISSON_OK;
	}
	/* Maximum retransmission count is reached */
	/* Last message probably went missing ... */
	else if((rv & ((1 << MAX_RT))))
	{
		return NRF24_MESSAGE_LOST;
	}  
	/* Probably still sending ... */
	else
	{
		return 0xFF;
	}
}

uint8_t Nrf24::retransmissionCount()
{
	uint8_t rv;
	readRegister(OBSERVE_TX,&rv,1);
	rv = rv & 0x0F;
	return rv;
}

/* Returns the payload length */
uint8_t Nrf24::payloadLength()
{
	uint8_t status;
	set_CSN_LOW();
	spi_transfer(R_RX_PL_WID);
	status = spi_transfer(0x00);
	set_CSN_HIGH();
	return status;
}

/* power management */
void Nrf24::powerUpRx(){     
	set_CSN_LOW();
	spi_transfer(FLUSH_RX);
	set_CSN_HIGH();

	configRegister(STATUS,(1<<RX_DR)|(1<<TX_DS)|(1<<MAX_RT)); 

	set_CE_LOW();
	configRegister(CONFIG,nrf24_CONFIG|((1<<PWR_UP)|(1<<PRIM_RX)));    
	set_CE_HIGH();
}
void Nrf24::powerUpTx()
{
	configRegister(STATUS,(1<<RX_DR)|(1<<TX_DS)|(1<<MAX_RT)); 

	configRegister(CONFIG,nrf24_CONFIG|((1<<PWR_UP)|(0<<PRIM_RX)));
}

void Nrf24::powerDown()
{
	set_CE_LOW();
	configRegister(CONFIG,nrf24_CONFIG);
}

/* low level interface ... */
void Nrf24::transferSync(uint8_t* dataout,uint8_t* datain,uint8_t len)
{
	uint8_t i;

	for(i=0;i<len;i++)
	{
		datain[i] = spi_transfer(dataout[i]);
	}

}

/* send multiple bytes over SPI */
void Nrf24::transmitSync(uint8_t* dataout,uint8_t len)
{
	uint8_t i;

	for(i=0;i<len;i++)
	{
		spi_transfer(dataout[i]);
	}

}

/* Clocks only one byte into the given nrf24 register */
void Nrf24::configRegister(uint8_t reg, uint8_t value)
{
	set_CSN_LOW();
	spi_transfer(W_REGISTER | (REGISTER_MASK & reg));
	spi_transfer(value);
	set_CSN_HIGH();
}

/* Read single register from nrf24 */
void Nrf24::readRegister(uint8_t reg, uint8_t* value, uint8_t len)
{
	set_CSN_LOW();
	spi_transfer(R_REGISTER | (REGISTER_MASK & reg));
	transferSync(value,value,len);
	set_CSN_HIGH();
}

/* Write to a single register of nrf24 */
void Nrf24::writeRegister(uint8_t reg, uint8_t* value, uint8_t len) 
{
	set_CSN_LOW();
	spi_transfer(W_REGISTER | (REGISTER_MASK & reg));
	transmitSync(value,len);
	set_CSN_HIGH();
}