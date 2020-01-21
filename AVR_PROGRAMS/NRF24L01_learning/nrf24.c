/*
 * RF_Tranceiver.c
 *
 * Created: 2012-08-10 15:24:35
 *  Author: Kalle
 *  Atmega88       I need to edit to make it work for the attiny85
 */ 

#include <avr/io.h>
#include <stdio.h>
#define F_CPU 1000000UL   //this is for atmega88
//#define F_CPU 8000000UL  // 8 MHz   this is for atmega88 
#include <util/delay.h>
#include <avr/interrupt.h>

#include "nRF24L01.h"

#define dataLen 3  //längd på datapacket som skickas/tas emot
uint8_t *data;
uint8_t *arr;


/*****************ändrar klockan till 8MHz ist för 1MHz*****************************/
void clockprescale(void)	
{
	CLKPR = 0b10000000;	//Prepare the chip for a change of clock prescale (CLKPCE=1 and the rest zeros)
	CLKPR = 0b00000000;	//Wanted clock prescale (CLKPCE=0 and the four first bits CLKPS0-3 sets division factor = 1)
	//See page 38 in datasheet
}
////////////////////////////////////////////////////


/*****************USART*****************************/  //Skickar data från chip till com-port simulator på datorn
//Initiering

void usart_init(void)
{
	DDRD |= (1<<1);	//Set TXD (PD1) as output for USART
	
	unsigned int USART_BAUDRATE = 9600;		//Same as in "terminal.exe"
	unsigned int ubrr = (((F_CPU / (USART_BAUDRATE * 16UL))) - 1);	//baud prescale calculated according to F_CPU-define at top
	
	/*Set baud rate */
	UBRR0H = (unsigned char)(ubrr>>8);
	UBRR0L = (unsigned char)ubrr;
	
	/*	Enable receiver and transmitter */
	UCSR0B = (1<<RXEN0)|(1<<TXEN0);

	/* Set frame format: 8data, 2stop bit, The two stop-bits does not seem to make any difference in my case!?*/
	UCSR0C = (1<<USBS0)|(3<<UCSZ00);
	
}



//Funktionen som skickar iväg byten till datorn

void USART_Transmit(uint8_t data)
{
	/* Wait for empty transmit buffer */
	while ( !( UCSR0A & (1<<UDRE0)) );
	/* Put data into buffer, sends the data */
	UDR0 = data;
}

//Funktionen som Tar emot kommandon av datorn som senare ska skickas till transmittern


uint8_t USART_Receive( void )
{
	/* Wait for data to be received */
	while ( !(UCSR0A & (1<<RXC0)) );	//This loop is only needed if you not use the interrupt...
	
	/* Get and return received data from buffer */
	return UDR0; //Return the received byte
}

/*****************SPI*****************************/  //Skickar data mellan chip och nrf'ens chip
//initiering
/*
void InitSPI(void)  // atmega88
{
	//Set SCK (PB5), MOSI (PB3) , CSN (SS & PB2) & C  as outport 
	//OBS!!! Måste sättas innan SPI-Enable neadn
	DDRB |= (1<<DDB5) | (1<<DDB3) | (1<<DDB2) |(1<<DDB1);
	
	// Enable SPI, Master, set clock rate fck/16 .. kan ändra hastighet utan att det gör så mycket
	SPCR |= (1<<SPE)|(1<<MSTR);// |(1<<SPR0) |(1<<SPR1);
	
	SETBIT(PORTB, 2);	//CSN IR_High to start with, vi ska inte skicka nåt till nrf'en ännu!
	CLEARBIT(PORTB, 1);	//CE low to start with, nrf'en ska inte sända/ta emot nåt ännu!
}
*/


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


//Skickar kommando till nrf'en å får då tillbaka en byte
/*
char WriteByteSPI(unsigned char cData) //for attiny88
{
	//Load byte to Data register
	SPDR = cData;	
		
	// Wait for transmission complete 
	while(!(SPSR & (1<<SPIF)));
	
	//Returnera det som sänts tillbaka av nrf'en (första gången efter csn-låg kommer Statusregistert)
	return SPDR;
}
////////////////////////////////////////////////////
*/

uint8_t WriteByteSPI(uint8_t cData){
	//load data to data register
	USIDR = cData;
	USISR |= (1 << USIOIF);  //clear flag to be able to receive new data
	
	//wait for transmission complete
	while((USISR & (1 << USIOIF)) == 0){
		USCIR |= (1 << USITC); //toggle SCK and count a 4 bit counter from 0 to 1, when it reaches 15 USIOIF set!
	}
	return USIDR;
} 

/*****************in/out***************************/  //ställ in t.ex. LED
//sätter alla I/0 portar för t.ex. LED
void ioinit(void)			
{
	DDRB |= (1<<DDB0); //led
}
////////////////////////////////////////////////////


/*****************interrupt***************************/ //orsaken till att köra med interrupt är att de avbryter koden var den än är och kör detta som är viktigast!
//när data tas emot/skickas så går interr uptet INT0 näst längst ner igång
void INT0_interrupt_init(void)	
{
	DDRD &= ~(1<<DDD2);	//Extern interrupt på INT0, dvs sätt den till input!
	
	EICRA |=  (1<<ISC01);// INT0 falling edge	PD2
	EICRA  &=  ~(1<<ISC00);// INT0 falling edge	PD2

	EIMSK |=  (1<<INT0);	//enablar int0
  	//sei();              // Enable global interrupts görs sen
} 

//när chipets RX (usart) får ett meddelande fårn datorn går interruptet USART_RX igång längst ner.

void USART_interrupt_init(void)
{
	UCSR0B |= (1<<RXCIE0);	//Enable interrupt that triggers on USART-data is received,
}

//////////////////////////////////////////////////////

//funktion för att hämta nåt av nrf's register
/*
uint8_t GetReg(uint8_t reg)
{	
	//andvändning: USART_Transmit(GetReg(STATUS)); //där status är registret du vill kolla
	_delay_us(10);
	CLEARBIT(PORTB, 2);	//CSN low
	_delay_us(10);
	WriteByteSPI(R_REGISTER + reg);	//Vilket register vill du läsa (nu med R_Register för att inget ska skrivas till registret)
	_delay_us(10);
	reg = WriteByteSPI(NOP);	//Skicka NOP antalet byte som du vill hämta (oftast 1gång, men t.ex addr är 5 byte!) och spara isf inte i "reg" utan en array med en loop
	_delay_us(10);
	SETBIT(PORTB, 2);	//CSN IR_High
	return reg;	// Returnerar registret förhoppningsvis med bit5=1 (tx_ds=lyckad sändning)
}
*/

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
/* This is just note code so I can understand the protocol, the more advanced form is based on this one
	void WriteToNrf(uint8_t reg, uint8_t Package)
	{	
		_delay_us(10); //make sure last command was a while ago
		CLEARBIT(PORTB, PB4);  //CSN low - nRF starts to listen for Command
		
		_delay_us(10);
		WriteByteSPI(W_REGISTER + reg); //W_register = set the nrf to write mode, 'reg' the registry to be read back (the register to be read back?)
		_delay_us(10);
		WriteByteSPI(Package); //send the package to be written to the 'reg' registry 
		
		_delay_us(10);
		SETBIT(PORTB, PB4); //CSN Hi - nRF goes back to doing nothing

	}
*/
/*****************nrf-setup***************************/ //Ställer in nrf'en genoma att först skicka vilket register, sen värdet på registret.
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
/*
	for atmega88
	uint8_t *WriteToNrf(uint8_t ReadWrite, uint8_t reg, uint8_t *val, uint8_t antVal)	//tar in "ReadWrite" (W el R), "reg" (ett register), "*val" (en array) & "antVal" (antal integer i variabeln)
	{
		cli();	//disable global interrupt
	
		if (ReadWrite == W)	//W=vill skriva till nrf-en (R=läsa av den, R_REGISTER (0x00) ,så skiter i en else funktion)
		{
			reg = W_REGISTER + reg;	//ex: reg = EN_AA: 0b0010 0000 + 0b0000 0001 = 0b0010 0001  
		}
	
		//Static uint8_t för att det ska gå att returnera en array (lägg märke till "*" uppe på funktionen!!!)
		static uint8_t ret[dataLen];	//antar att det längsta man vill läsa ut när man kallar på "R" är dataleng-långt, dvs använder man bara 1byte datalengd å vill läsa ut 5byte RF_Adress så skriv 5 här ist!!!	
	
		_delay_us(10);		//alla delay är så att nrfen ska hinna med! (microsekunder)
		CLEARBIT(PORTB, 2);	//CSN low = nrf-chippet börjar lyssna
		_delay_us(10);		
		WriteByteSPI(reg);	//första SPI-kommandot efter CSN-låg berättar för nrf'en vilket av dess register som ska redigeras ex: 0b0010 0001 write to registry EN_AA	
		_delay_us(10); 		
	
		int i;
		for(i=0; i<antVal; i++)
		{
			if (ReadWrite == R && reg != W_TX_PAYLOAD)
			{
				ret[i]=WriteByteSPI(NOP);	//Andra och resten av SPI kommandot säger åt nrfen vilka värden som i det här fallet ska läsas
				_delay_us(10);			
			}
			else 
			{
				WriteByteSPI(val[i]);	//Andra och resten av SPI kommandot säger åt nrfen vilka värden som i det här fallet ska skrivas till
				_delay_us(10);
			}		
		}
		SETBIT(PORTB, 2);	//CSN IR_High = nrf-chippet slutar lyssna
	
		sei(); //enable global interrupt
	
		return ret;	//returnerar en array
	}
*/
//initierar nrf'en (obs nrfen måste vala i vila när detta sker CE-låg)


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
	val[0]=0x01;  //
	WriteToNrf(W, RF_CH, val, 1); //RF channel registry 0b0000 0001 = 2,401GHz (same on TX å RX)

	//RF setup	- selects power and transmission speed, the + version of nrf better
	val[0]=0x07;
	WriteToNrf(W, RF_SETUP, val, 1); //00000111 bit 3="0"gives lower transmission speed 1Mbps = Longer range, bit 2-1 gives power mode high (-0dB) ("11" = (- 18dB) gives lower power = current lesser but lower range)
	//"11" = -0db, "00" = -18db for bit 2-1 power mode

	// RX RF_Adress setup 5 bytes - selects the RF_Address on the Recivern (Must be given the same RF_Adress if the Transmitter has EN_AA switched on !!!) RX_ADDR_P0 = TX_ADDRif EN_AA enabled
	int i;
	for(i=0; i<5; i++)	
	{
		val[i]=0x12;	// RF channel registry 0b10101011 x 5 - writes the same RF_Adress 5ggr to get an easy and secure RF_Adress (same on the transmitter's chip !!!
	}
	WriteToNrf(W, RX_ADDR_P0, val, 5); // 0b0010 1010 write registry - since we chose pipe 0 in "EN_RXADDR" above, we give the RF_Address to this pipe. (can give different RF_Addresses to different pipes and thus listen to different transmitters only if they are enabled on EN_RXADDR)
	
	
	// TX RF_Adress setup 5 bytes - selects the RF_Address on the Transmitter (can be commented on on a "clean" Reciver) 
	// int i; // reuse previous in ...
	//set Transmitter  address not used in receiver but good to set it anyway in case of dynamic switch 
	for(i=0; i<5; i++)	
	{
		val[i]=0x12;	// RF channel registry 0b10111100 x 5 - writes the same RF_Adress 5ggr to get an easy and secure RF_Adress (same on receiver chip and on the RX-RF_Address above if EN_AA enabled !!!)
	}
	WriteToNrf(W, TX_ADDR, val, 5); 

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
/*	void nrf24L01_init(void)
	{
		_delay_ms(100);	//allow radio to reach power down if shut down
	
		uint8_t val[5];	//en array av integers som skickar värden till WriteToNrf-funktionen

		//EN_AA - (auto-acknowledgements) - Transmittern får svar av recivern att packetet kommit fram, grymt!!! (behöver endast vara enablad på Transmittern!)
		//Kräver att Transmittern även har satt SAMMA RF_Adress på sin mottagarkanal nedan ex: RX_ADDR_P0 = TX_ADDR
		val[0]=0x01;	//ger första integern i arrayen "val" ett värde: 0x01=EN_AA på pipe P0. 
		WriteToNrf(W, EN_AA, val, 1);	//W=ska skriva/ändra nåt i nrfen, EN_AA=vilket register ska ändras, val=en array med 1 till 32 värden  som ska skrivas till registret, 1=antal värden som ska läsas ur "val" arrayen.
	
		//SETUP_RETR (the setup for "EN_AA")
		val[0]=0x2F;	//0b0010 00011 "2" sets it up to 750uS delay between every retry (at least 500us at 250kbps and if payload >5bytes in 1Mbps, and if payload >15byte in 2Mbps) "F" is number of retries (1-15, now 15)
		WriteToNrf(W, SETUP_RETR, val, 1);
	
		//Väljer vilken/vilka datapipes (0-5) som ska vara igång.
		val[0]=0x01;
		WriteToNrf(W, EN_RXADDR, val, 1); //enable data pipe 0

		//RF_Adress width setup (hur många byte ska RF_Adressen bestå av? 1-5 bytes) (5bytes säkrare då det finns störningar men långsammare dataöverföring) 5addr-32data-5addr-32data....
		val[0]=0x03;
		WriteToNrf(W, SETUP_AW, val, 1); //0b0000 00011 motsvarar 5byte RF_Adress

		//RF channel setup - väljer frekvens 2,400-2,527GHz 1MHz/steg
		val[0]=0x01;
		WriteToNrf(W, RF_CH, val, 1); //RF channel registry 0b0000 0001 = 2,401GHz (samma på TX å RX)

		//RF setup	- väljer effekt och överföringshastighet 
		val[0]=0x07;
		WriteToNrf(W, RF_SETUP, val, 1); //00000111 bit 3="0" ger lägre överföringshastighet 1Mbps=Längre räckvidd, bit 2-1 ger effektläge hög (-0dB) ("11"=(-18dB) ger lägre effekt =strömsnålare men lägre range)

		//RX RF_Adress setup 5 byte - väljer RF_Adressen på Recivern (Måste ges samma RF_Adress om Transmittern har EN_AA påslaget!!!)
		int i;
		for(i=0; i<5; i++)	
		{
			val[i]=0x12;	//RF channel registry 0b10101011 x 5 - skriver samma RF_Adress 5ggr för att få en lätt och säker RF_Adress (samma på transmitterns chip!!!)
		}
		WriteToNrf(W, RX_ADDR_P0, val, 5); //0b0010 1010 write registry - eftersom vi valde pipe 0 i "EN_RXADDR" ovan, ger vi RF_Adressen till denna pipe. (kan ge olika RF_Adresser till olika pipes och därmed lyssna på olika transmittrar) 	
	
		//TX RF_Adress setup 5 byte -  väljer RF_Adressen på Transmittern (kan kommenteras bort på en "ren" Reciver)
		//int i; //återanvänder föregående i...
		for(i=0; i<5; i++)	
		{
			val[i]=0x12;	//RF channel registry 0b10111100 x 5 - skriver samma RF_Adress 5ggr för att få en lätt och säker RF_Adress (samma på Reciverns chip och på RX-RF_Adressen ovan om EN_AA enablats!!!)
		}
		WriteToNrf(W, TX_ADDR, val, 5); 

		// payload width setup - Hur många byte ska skickas per sändning? 1-32byte 
		val[0]=dataLen;		//"0b0000 0001"=1 byte per 5byte RF_Adress  (kan välja upp till "0b00100000"=32byte/5byte RF_Adress) (definierat högst uppe i global variabel!)
		WriteToNrf(W, RX_PW_P0, val, 1);
	
		//CONFIG reg setup - Nu är allt inställt, boota upp nrf'en och gör den antingen Transmitter lr Reciver
		val[0]=0x1E;  //0b0000 1110 config registry	bit "1":1=power up,  bit "0":0=transmitter (bit "0":1=Reciver) (bit "4":1=>mask_Max_RT,dvs IRQ-vektorn reagerar inte om sändningen misslyckades. 
		WriteToNrf(W, CONFIG, val, 1);

	//device need 1.5ms to reach standby mode
		_delay_ms(100);	

		//sei();	
	}
*/

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


/////////////////////////////////////////////////////

int main(void)
{
	clockprescale();
	usart_init();
	InitSPI();
    ioinit();
	INT0_interrupt_init();
	USART_interrupt_init();

	nrf24L01_init();

	SETBIT(PORTB,0);		//För att se att dioden fungerar!
	_delay_ms(1000);
	CLEARBIT(PORTB,0);
	
	while(1)
	{
		//Wait for USART-interrupt to send data...

	}
	return 0;
}




ISR(INT0_vect)	//vektorn som går igång när transmit_payload lyckats sända eller när receive_payload fått data OBS: då Mask_Max_rt är satt i config registret så går den inte igång när MAX_RT är uppnåd å sändninge nmisslyckats!
{
	cli();	//Disable global interrupt
	CLEARBIT(PORTB, 1);		//ce låg igen -sluta lyssna/sända
	
	SETBIT(PORTB, 0); //led on
	_delay_ms(500);
	CLEARBIT(PORTB, 0); //led off
	
	//Receiver function to print out on usart:
	//data=WriteToNrf(R, R_RX_PAYLOAD, data, dataLen);	//läs ut mottagen data
	//reset();
//
	//for (int i=0;i<dataLen;i++)
	//{
		//USART_Transmit(data[i]);
	//}
	//
	sei();

}

ISR(USART_RX_vect)	///Vector that triggers when computer sends something to the Atmega88
{
	uint8_t W_buffer[dataLen];	//Creates a buffer to receive data with specified length (ex. dataLen = 5 bytes)
	
	int i;
	for (i=0;i<dataLen;i++)
	{
		W_buffer[i]=USART_Receive();	//receive the USART
		USART_Transmit(W_buffer[i]);	//Transmit the Data back to the computer to make sure it was correctly received
		//This probably should wait until all the bytes is received, but works fine in to send and receive at the same time... =)
	}
	
	reset();	//reset irq - kan skicka data på nytt
	
	if (W_buffer[0]=='9')	//om projektorduk
	{
		ChangeAddress(0x13);	//change address to send to different receiver
		transmit_payload(W_buffer);	//Sänder datan
		ChangeAddress(0x12);	//tillbaka till ultimata fjärrisen
	} 
	else
	{
		transmit_payload(W_buffer);	//Sänder datan
	}
	
	USART_Transmit('#');	//visar att chipet mottagit datan...
	
}