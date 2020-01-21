/*
 * RF_Tranceiver.c
 *
 * Created: 2012-08-10 15:24:35
 *  Author: Kalle
 *  Atmega88       I need to edit to make it work for the atmega88
 */ 

#include <avr/io.h>
#include <stdio.h>
//#define F_CPU 1000000UL   //this is for atmega88
//#define F_CPU 8000000UL  // 8 MHz   this is for atmega88 
#include <util/delay.h>
#include <avr/interrupt.h>

#include "nRF24L01.h"

#define dataLen 32  // length of the data packet sent / received
uint8_t *data;
uint8_t *arr;
uint8_t tx_address[5] = {0xE7,0xE7,0xE7,0xE7,0xE7};
uint8_t rx_address[5] = {0xD7,0xD7,0xD7,0xD7,0xD7};

void InitSPI(void){    //attiny 85
	//set SCK (PB2), MISO(PB1 connects to nRF MOSI),  CSN(PB4), CE (PB3) as outport
	//OBS!! Has to be set before SPI-enable below!
	DDRB |= (1 << PB2) | (1 << PB1) | (1 << PB4) | (1 << PB3);
	
	//set mosi PBO as input OBS, connects to nRF MISO
	DDRB &= ~ (1 << PB0);
	PORTB |= (1 <<PB0);
	
	USICR |= (1 << USIWM0) | (1 << USICS1) | (1 << USICLK);  //this is SPI enable, or in other words USI because of Attiny85
	
	SETBIT(PORTB,4); //CSN high to start with nothing has to be sent to nrf as of yet
	CLEARBIT(PORTB,3); //CE low to start with, nothing to send/receive yet
}

uint8_t WriteByteSPI(uint8_t cData){
	//load data to data register
	USIDR = cData;
	USISR |= (1 << USIOIF);  //clear flag to be able to receive new data
	
	//wait for transmission complete
	while((USISR & (1 << USIOIF)) == 0){
		USICR |= (1 << USITC); //toggle SCK and count a 4 bit counter from 0 to 1, when it reaches 15 USIOIF set!
	}
	return USIDR;
}

uint8_t GetReg(uint8_t reg)
{	
	_delay_us(10); //make sure last command was a while ago
	CLEARBIT(PORTB, PB4);  //CSN low - nRF starts to listen for Command
	_delay_us(10);
	WriteByteSPI(R_REGISTER + reg); //R_register = set the nrf to reading mode, 'reg' the registry to be read back (the register to be read back?)
	_delay_us(10);
	reg = WriteByteSPI(NOP); //send NOP (dummy byte) once to receive back the first byte of the 'reg' register
	_delay_us(10);
	SETBIT(PORTB, PB4); //CSN Hi - nRF goes back to doing nothing
	return reg; //return the read registry
}

uint8_t *WriteToNrf(uint8_t ReadWrite, uint8_t reg, uint8_t *val, uint8_t antVal)	//tar in "ReadWrite" (W el R), "reg" (ett register), "*val" (en array) & "antVal" (antal integer i variabeln)
{
	//this function version is for attiny85
	//cli();	//disable global interrupt
	//readwrite ("W" or "R"), "reg" the registry, "*val" an array with the package  & "antVal" number of integers in the package
	
	if (ReadWrite == W)	//if W then you want to write to the nrf (read mode "R" == 0x00, so that's why its left out in this version)
	{
		reg = W_REGISTER + reg;	//ex: reg = EN_AA: 0b0010 0000 + 0b0000 0001 = 0b0010 0001       
		//add the write bit to the reg 
	}
	
	
	static uint8_t ret[dataLen];	//create an array to be returned at the end, static array needed to return, static to reduce resource consumption	
	
	_delay_us(10);		//make sure last command was a while ago
	CLEARBIT(PORTB, PB4);	//CSN low - nRF starts to listen for Command
	_delay_us(10);		
	WriteByteSPI(reg);	//set the nrF to write or read mode of reg	
	_delay_us(10); 		
	
	int i;
	for(i=0; i<antVal; i++)
	{
		if (ReadWrite == R && reg != W_TX_PAYLOAD)   //did you want to read a registry?
		{											//When writing to W_TX_Payload cannot add the W because its on the same "level"in the registry 
			ret[i]=WriteByteSPI(NOP);	//send dummy bytes to read out the registry
			_delay_us(10);			
		}
		else 
		{
			WriteByteSPI(val[i]);	//send commands to nRF one at a time
			_delay_us(10);
		}		
	}
	SETBIT(PORTB, PB4);	//CSN IR_High = nrf-goes back to doing nothing
	
	//sei(); //enable global interrupt
	
	return ret;	//returnerar en array
}

void nrf24L01_init(void)
{
	_delay_ms(100);	//allow radio to reach power down if shut down
	
	uint8_t val[5];	//array of av integers to be sent to writetonrf function

	//EN_AA - (enable auto-acknowledgements) - Transmitter gets automatic response from receiver when successful transmission! 
	//Only works if  Transmitter has identical RF_Address on is channel: RX_ADDR_P0 = TX_ADDR
	val[0]=0x01;	//gives the first integer in the "selection" array a value: 0x01=EN_AA on pipe P0. 
	WriteToNrf(W, EN_AA, val, 1);	// W = should write / change something in nrfen, EN_AA = which register should be changed, val = an array with 1 to 32 values ​​to be written to the register, 1 = number of values ​​to read from the "selection" array.
	
	//SETUP_RETR (the setup for "EN_AA")
	val[0]=0x2F;	//0b0010 00011 "2" sets it up to 750uS delay between every retry (at least 500us at 250kbps and if payload >5bytes in 1Mbps, and if payload >15byte in 2Mbps) "F" is number of retries (1-15, now 15)
	WriteToNrf(W, SETUP_RETR, val, 1); //setup retries
	
	//choose number of enables pipes (1-5)
	val[0]=0x01;
	WriteToNrf(W, EN_RXADDR, val, 1); //enable data pipe 0

	// RF_Adress width setup (how many bytes should the RF_Address consist of? 1-5 bytes) (5 bytes safer when there are interference but slower data transmission) 5addr-32data-5addr-32data ....
	val[0]=0x03;//0b0000 00011  = 5 bytes RF_Adress
	WriteToNrf(W, SETUP_AW, val, 1); 

	//RF channel setup choose frequency 2,400-2,527GHz 1MHz/steg
	val[0]=0x02;  //
	WriteToNrf(W, RF_CH, val, 1); //RF channel registry 0b0000 0001 = 2,401GHz (same on TX å RX)

	//RF setup	- selects power and transmission speed, the + version of nrf better
	val[0]=0x07;
	WriteToNrf(W, RF_SETUP, val, 1); //00000111 bit 3="0"gives lower transmission speed 1Mbps = Longer range, bit 2-1 gives power mode high (-0dB) ("11" = (- 18dB) gives lower power = current lesser but lower range)
	//"11" = -0db, "00" = -18db for bit 2-1 power mode

	// RX RF_Adress setup 5 bytes - selects the RF_Address on the Recivern (Must be given the same RF_Adress if the Transmitter has EN_AA switched on !!!) RX_ADDR_P0 = TX_ADDRif EN_AA enabled
	/*int i;
	for(i=0; i<5; i++)	
	{
		val[i]=0x12;	// RF channel registry 0b10101011 x 5 - writes the same RF_Adress 5ggr to get an easy and secure RF_Adress (same on the transmitter's chip !!!
	}*/
	WriteToNrf(W, RX_ADDR_P0, rx_address, 5); // 0b0010 1010 write registry - since we chose pipe 0 in "EN_RXADDR" above, we give the RF_Address to this pipe. (can give different RF_Addresses to different pipes and thus listen to different transmitters only if they are enabled on EN_RXADDR)
	
	
	// TX RF_Adress setup 5 bytes - selects the RF_Address on the Transmitter (can be commented on on a "clean" Reciver) 
	// int i; // reuse previous in ...
	//set Transmitter  address not used in receiver but good to set it anyway in case of dynamic switch 
	/*for(i=0; i<5; i++)	
	{
		val[i]=0x12;	// RF channel registry 0b10111100 x 5 - writes the same RF_Adress 5ggr to get an easy and secure RF_Adress (same on receiver chip and on the RX-RF_Address above if EN_AA enabled !!!)
	}*/
	WriteToNrf(W, TX_ADDR, tx_address, 5); 

	// payload width setup - How many bytes to send in transmission? 1-32byte 
	val[0]=dataLen;		// "0b0000 0001" = 1 byte per 5 byte RF_Address (can choose up to "0b00100000" = 32 byte / 5 byte RF_Adress) (defined at the top of global variable!
	WriteToNrf(W, RX_PW_P0, val, 1);
	
	//CONFIG reg setup - Now its time to boot up the nrf and choose if its suppose to be a transmitter or receiver
	val[0]=0x1E;  // 0b0000 1110 config registry bit "1": 1 = power up, bit "0": 0 = transmitter (bit "0": 1 = Reciver) (bit "4": 1 => mask_Max_RT, ie the IRQ vector does not respond if the transmission failed.
	WriteToNrf(W, CONFIG, val, 1);

	//device need 1.5ms to reach standby mode
	_delay_ms(100);	

	//sei();	
}
void ChangeAddress(uint8_t adress)
{
	_delay_ms(100);
	uint8_t val[5];
	// RX RF_Adress setup 5 bytes - selects the RF_Address on the Recivern (Must be given the same RF_Adress if the Transmitter has EN_AA switched on !!!)

	int i;
	for(i=0; i<5; i++)
	{
		val[i]=adress;	// RF channel registry 0b10101011 x 5 - writes the same RF_Adress 5ggr to get an easy and secure RF_Adress (same on the transmitter's chip !!!)
	}
	WriteToNrf(W, RX_ADDR_P0, val, 5); // 0b0010 1010 write registry - since we chose pipe 0 in "EN_RXADDR" above, we give the RF_Address to this pipe. (can give different RF_Addresses to different pipes and thus listen to different transmitters)
	

	// TX RF_Adress setup 5 bytes - selects the RF_Address on the Transmitter (can be commented on on a "clean" Reciver)
	// int i; // reuse previous in ...
	for(i=0; i<5; i++)
	{
		val[i]=adress;	
// RF channel registry 0b10111100 x 5 - writes the same RF_Adress 5ggr to get an easy and secure RF_Adress (same on receiver chip and on the RX-RF_Address above about EN_AA enabled !!!)
	}
	WriteToNrf(W, TX_ADDR, val, 5);
	_delay_ms(100);
}
/////////////////////////////////////////////////////

/*****************Funktioner***************************/ 
// Functions used in main
// Resets the nrf for new communication
void reset(void)
{
	_delay_us(10);
	CLEARBIT(PORTB, PB4);	//CSN low
	_delay_us(10);
	WriteByteSPI(W_REGISTER + STATUS);	//
	_delay_us(10);
	WriteByteSPI(0b01110000);	// erases all irq in the status register (to be able to listen again)
	_delay_us(10);
	SETBIT(PORTB, PB4);	//CSN IR_High
}

//Reciverfunktioner
/*********************Reciverfunktioner********************************/
// opens Recivern and "Listens" in 1s
void receive_payload(void)
{
	//sei();		//Enable global interrupt
	
	SETBIT(PORTB, PB3);	//CE IR_High = "listen" 
	_delay_ms(1000);	// listens in 1s and if received, int0 interrupt vector goes on
	CLEARBIT(PORTB, PB3); //ce low re-connect listen

	
	//cli();	//Disable global interrupt
}

//Sänd data
void transmit_payload(uint8_t * W_buff)
{
	WriteToNrf(R, FLUSH_TX, W_buff, 0); // sends 0xE1 which flushes the registry so that old data should not wait to be sent when you want to send new data! R stands for W_REGISTER not to be added. sends no command betrothed because it is not needed! W_buff [] is only there because an array must exist ...
	
	WriteToNrf(R, W_TX_PAYLOAD, W_buff, dataLen);	// sends the data in W_buff to the nrf-one (note that you cannot read the w_tx_payload register !!!)
	
	//sei();	//enable global interrupt-already on in atmega88 version of code!
	//USART_Transmit(GetReg(STATUS));

	_delay_ms(10);		// does it really need ms to not us ??? YEEES! otherwise it doesn't work !!!
	SETBIT(PORTB, PB3);	// CE high = transmitted data INT0 interrupt is executed when the transmission is successful and if EN_AA is on, the response from the receiver is also received
	_delay_us(20);		// at least 10us!
	CLEARBIT(PORTB, PB3);	//CE low
	_delay_ms(10);		// does it really need ms to not us ??? YEEES! otherwise it doesn't work !!!


	//cli();	//Disable global interrupt... ajabaja, then the USART_RX listening closes!


}

int main(void)
{

	InitSPI();
	nrf24L01_init();
	uint8_t pay_load[dataLen];
	for(int i = 0; i < dataLen; i++){
		pay_load[i] = 0;
	}
	//char * string = "hello world!";
	
	//for(int i = 0; string[i] != 0; i++){
	//	pay_load[i] = string[i];
	//}
	//pay_load[14] = 0;
	//uint8_t c = 'A';
	while(1)
	{
		
		//c = (c - 'A') % 26 + 'A';
		//pay_load[13] = c;
		transmit_payload(pay_load);
		reset();
		_delay_ms(10);
		//c++;
	}
	return 0;
}