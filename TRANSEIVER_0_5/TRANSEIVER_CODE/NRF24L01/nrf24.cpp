/* adjustment functions */
#include "nrf24.h"

Nrf24::Nrf24(){
	
}

void Nrf24::init(){
		//hmmmmmm
		for(uint8_t i = 0; i < 5; i++){
			RX_ADDR_P_VAL[0] = rand() % 255;
		}
		
		standardSPIPinInit();
		set_CE(LOW);
		set_CSN(HIGH);
}

void Nrf24::standardConfig(){
	payload_len = 32;
    
    configRegister(RF_CH,2);
	configRegister(SETUP_AW, 0x03); //decides the address width its 5 bytes by default
	//the other settings are defaulted
    // Set length of incoming payload 
    for(int i = 0; i < 6; i++){
    	set_RX_address(RX_ADDR_P_VAL[i], i);
    }
    set_TX_address(TX_ADDR_VAL);
    configRegister(RX_PW_P0, payload_len); // Auto-ACK pipe ... defaulting to 32 for now
    configRegister(RX_PW_P1, payload_len); // Data payload pipe
    configRegister(RX_PW_P2, payload_len); // Pipe not used 
    configRegister(RX_PW_P3, payload_len); // Pipe not used 
    configRegister(RX_PW_P4, payload_len); // Pipe not used 
    configRegister(RX_PW_P5, payload_len); // Pipe not used 

    // 250 kbps, TX gain: 0dbm already at max       
    configRegister(RF_SETUP, (0 << RF_DR_HIGH)|((0x03)<<RF_PWR)); //this not configuring right?

    // CRC enable, 1 byte CRC length
    configRegister(CONFIG,nrf24_CONFIG); //this looks like an error ((1<<EN_CRC)|(0<<CRCO))
    

    // Auto Acknowledgment
    configRegister(EN_AA,(0<<ENAA_P0)|(0<<ENAA_P1)|(0<<ENAA_P2)|(0<<ENAA_P3)|(0<<ENAA_P4)|(0<<ENAA_P5)); //might need to create an interrupt

    // Enable RX addresses
    configRegister(EN_RXADDR,(1<<ERX_P0)|(1<<ERX_P1)|(1<<ERX_P2)|(1<<ERX_P3)|(1<<ERX_P4)|(1<<ERX_P5));

    // Auto retransmit delay: 1000 us and Up to 15 retransmit trials
    //configRegister(SETUP_RETR,(0x04<<ARD)|(0x0F<<ARC));
	
    // Dynamic length configurations: No dynamic length
    configRegister(DYNPD,(0<<DPL_P0)|(0<<DPL_P1)|(0<<DPL_P2)|(0<<DPL_P3)|(0<<DPL_P4)|(0<<DPL_P5));

    // Start listening
    //powerUpRx();
	
}

void Nrf24::set_RX_address(uint8_t * adr, uint8_t pipe){
	set_CE(LOW);
	switch(pipe){
		case 0:
				writeRegister(RX_ADDR_P0,adr,nrf24_ADDR_LEN);
				break;
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

	set_CE(HIGH);

}

uint8_t * Nrf24::get_RX_address(uint8_t pipe){
	static uint8_t buffer[5];
	buffer[0] = 0;
	buffer[1] = 0;
	buffer[2] = 0;
	buffer[3] = 0;
	buffer[4] = 0;
	switch(pipe){
		case 0: readRegister(RX_ADDR_P0, buffer, 5);
				break;
		case 1: readRegister(RX_ADDR_P1, buffer, 5);
				break;
		case 2: readRegister(RX_ADDR_P2, buffer + 4, 1);
				break;
		case 3: readRegister(RX_ADDR_P3, buffer + 4, 1);
				break;
		case 4: readRegister(RX_ADDR_P4, buffer + 4, 1);
				break;
		case 5: readRegister(RX_ADDR_P5, buffer + 4, 1);
				break;
		default:
				break;
	}
	static uint8_t * buffer_ptr = (uint8_t *) buffer;
	return buffer_ptr;
}


void Nrf24::set_TX_address(uint8_t* adr){
	/* RX_ADDR_P0 must be set to the sending addr for auto ack to work. */
	writeRegister(RX_ADDR_P0,adr,nrf24_ADDR_LEN); 
	writeRegister(TX_ADDR,adr,nrf24_ADDR_LEN);
}

uint8_t * Nrf24::get_TX_address(){
	static uint8_t buffer[5];
	readRegister(TX_ADDR, buffer, 5);
	static uint8_t * buffer_ptr = (uint8_t *) buffer;
	return buffer_ptr;
}


void Nrf24::set_CONFIG_Register(uint8_t value){
	configRegister(CONFIG,value);
}

uint8_t Nrf24::get_CONFIG_Register(){
	static uint8_t reg = 0;
	readRegister(CONFIG, &reg, 1);
	return reg;
}

void Nrf24::set_EN_AA_Register(uint8_t value){
	configRegister(EN_AA,value);
}

uint8_t Nrf24::get_EN_AA_Register(){
	static uint8_t reg = 0;
	readRegister(EN_AA, &reg, 1);
	return reg;
}

void Nrf24::set_EN_RXADDR_Register(uint8_t value){
	configRegister(EN_RXADDR, value);
}
uint8_t Nrf24::get_EN_RXADDR_Register(){
	static uint8_t reg = 0;
	readRegister(EN_RXADDR, &reg, 1);
	return reg;
}

void Nrf24::set_SETUP_AW_Register(uint8_t value){
	configRegister(SETUP_AW, value);
}

uint8_t Nrf24::get_SETUP_AW_Register(){
	static uint8_t reg = 0;
	readRegister(SETUP_AW, &reg, 1);
	return reg;
}

void Nrf24::set_SETUP_RETR_Register(uint8_t value){
	configRegister(SETUP_RETR, value);
}
uint8_t Nrf24::get_SETUP_RETR_Register(){
	static uint8_t reg = 0;
	readRegister(SETUP_RETR, &reg, 1);
	return reg;
}

void Nrf24::set_RF_CH_Register(uint8_t value){
	configRegister(RF_CH, value);
}

uint8_t Nrf24::get_RF_CH_Register(){
	static uint8_t reg = 0;
	readRegister(RF_CH, &reg, 1);
	return reg;
}

void Nrf24::set_RF_SETUP_Register(uint8_t value){
	configRegister(RF_SETUP,value);
}
uint8_t Nrf24::get_RF_SETUP_Register(){
	static uint8_t reg = 0;
	readRegister(RF_SETUP, &reg, 1);
	return reg;
}

void Nrf24::set_STATUS_Register(uint8_t value){
	configRegister(STATUS, value);
}

uint8_t Nrf24::get_STATUS_Register(){
	static uint8_t reg = 0;
	readRegister(STATUS, &reg, 1);
	return reg;
}

void Nrf24::set_OBSERVE_TX_Register(uint8_t value){
	configRegister(OBSERVE_TX, value);
}

uint8_t Nrf24::get_OBSERVE_TX_Register(){
	static uint8_t reg = 0;
	readRegister(OBSERVE_TX, &reg, 1);
	return reg;
}

void Nrf24::set_RX_PW_PN_Register(uint8_t value, uint8_t pipe){
	switch(pipe){
		case 0: configRegister(RX_PW_P0,value);
				break;
		case 1: configRegister(RX_PW_P1, value);
				break;
		case 2: configRegister(RX_PW_P2, value);
				break;
		case 3: configRegister(RX_PW_P3, value);
				break;
		case 4: configRegister(RX_PW_P4, value);
				break;
		case 5: configRegister(RX_PW_P5, value);
				break;
		default:
				break;
	}
}
uint8_t Nrf24::get_RX_PW_PN_Register(uint8_t pipe){
	static uint8_t reg = 0;
	switch(pipe){
		case 0: readRegister(RX_PW_P0, &reg, 1);
				break;
		case 1: readRegister(RX_PW_P1, &reg, 1);
				break;
		case 2: readRegister(RX_PW_P2, &reg, 1);
				break;
		case 3: readRegister(RX_PW_P3, &reg, 1);
				break;
		case 4: readRegister(RX_PW_P4, &reg, 1);
				break;
		case 5: readRegister(RX_PW_P5, &reg, 1);
				break;
		default:
				break;
	}
	return reg;
}

void Nrf24::set_FIFO_STATUS_Register(uint8_t value){
	configRegister(FIFO_STATUS, value);
}
uint8_t Nrf24::get_FIFO_STATUS_Register(){
	static uint8_t reg = 0;
	readRegister(FIFO_STATUS, &reg, 1);
	return reg;
}

void Nrf24::set_DYNPD_Register(uint8_t value){
	configRegister(DYNPD, value);
}

uint8_t Nrf24::get_DYNPD_Register(){
	static uint8_t reg = 0;
	readRegister(DYNPD, &reg, 1);
	return reg;
}


uint8_t Nrf24::isReceiving(){
	return receiving;
}

uint8_t Nrf24::isSuccessMode(){
	return success_mode;
}

void Nrf24::setSuccessMode(uint8_t value){
	success_mode = value;
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
	set_CSN(LOW);
	rv = spi_transfer(NOP);
	set_CSN(HIGH);
	return rv;
}


/* core TX / RX functions */
void Nrf24::send(uint8_t* value) {   
	/* Go to Standby-I first */
	set_CE(LOW);

	/* Set to transmitter mode , Power up if needed */
	powerUpTx();

	/* Do we really need to flush TX fifo each time ? */
	#if 1
		/* Pull down chip select */
		set_CSN(LOW);           

		/* Write cmd to flush transmit FIFO */
		spi_transfer(FLUSH_TX);     

		/* Pull up chip select */
		set_CSN(HIGH);                  
	#endif 

	/* Pull down chip select */
	set_CSN(LOW);

	/* Write cmd to write payload */
	spi_transfer(W_TX_PAYLOAD);

	/* Write payload */
	transmitSync(value,payload_len);   

	/* Pull up chip select */
	set_CSN(HIGH);

	/* Start the transmission */
	set_CE(HIGH);    
}


void Nrf24::getData(uint8_t* data) {
	/* Pull down chip select */
	set_CSN(LOW);                              

	/* Send cmd to read rx payload */
	spi_transfer( R_RX_PAYLOAD );

	/* Read payload */
	transferSync(data,data,payload_len);

	/* Pull up chip select */
	set_CSN(HIGH);

	/* Reset status register */
	configRegister(STATUS,(1<<RX_DR));   
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
	set_CSN(LOW);
	spi_transfer(R_RX_PL_WID);
	status = spi_transfer(0x00);
	set_CSN(HIGH);
	return status;
}

/* power management */
void Nrf24::powerUpRx(){
	receiving = TRUE;   
	set_CSN(LOW);
	spi_transfer(FLUSH_RX);
	set_CSN(HIGH);

	configRegister(STATUS,(1<<RX_DR)|(1<<TX_DS)|(1<<MAX_RT)); 

	set_CE(LOW);
	configRegister(CONFIG,nrf24_CONFIG|((1<<PWR_UP)|(1<<PRIM_RX)));    
	set_CE(HIGH);
}
void Nrf24::powerUpTx()
{
	receiving = FALSE;
	configRegister(STATUS,(1<<RX_DR)|(1<<TX_DS)|(1<<MAX_RT)); 

	configRegister(CONFIG,nrf24_CONFIG|((1<<PWR_UP)|(0<<PRIM_RX)));
}

void Nrf24::powerDown()
{
	receiving = FALSE;
	set_CE(LOW);
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
	set_CSN(LOW);
	spi_transfer(W_REGISTER | (REGISTER_MASK & reg));
	spi_transfer(value);
	set_CSN(HIGH);
}

/* Read single register from nrf24 */
void Nrf24::readRegister(uint8_t reg, uint8_t* value, uint8_t len)
{
	set_CSN(LOW);
	spi_transfer(R_REGISTER | (REGISTER_MASK & reg));
	transferSync(value,value,len);
	set_CSN(HIGH);
}

/* Write to a single register of nrf24 */
void Nrf24::writeRegister(uint8_t reg, uint8_t* value, uint8_t len) 
{
	set_CSN(LOW);
	spi_transfer(W_REGISTER | (REGISTER_MASK & reg));
	transmitSync(value,len);
	set_CSN(HIGH);
}