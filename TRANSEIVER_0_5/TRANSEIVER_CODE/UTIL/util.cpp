#include "util.h"


void printRegisters(Nrf24 &transeiver){
	uint8_t reg = 0;
	transeiver.readRegister(CONFIG, &reg, 1);
	printf(":CONFIG: %x\n", reg);

	reg = 0;
	transeiver.readRegister(EN_AA, &reg, 1);
	printf(":EN_AA: %x\n", reg);

	reg = 0;
	transeiver.readRegister(EN_RXADDR, &reg, 1);
	printf(":EN_RXADDR: %x\n", reg);

	reg = 0;
	transeiver.readRegister(SETUP_AW, &reg, 1);
	printf(":SETUP_AW: %x\n", reg);

	reg = 0;
	transeiver.readRegister(SETUP_RETR, &reg, 1);
	printf(":SETUP_RETR: %x\n", reg);

	reg = 0;
	transeiver.readRegister(RF_CH, &reg, 1);
	printf(":RF_CH: %x\n", reg);

	reg = 0;
	transeiver.readRegister(RF_SETUP, &reg, 1);
	printf(":RF_SETUP: %x\n", reg);

	reg = 0;
	transeiver.readRegister(STATUS, &reg, 1);
	printf(":STATUS: %x\n", reg);

	reg = 0;
	transeiver.readRegister(OBSERVE_TX, &reg, 1);
	printf(":OBSERVE_TX: %x\n", reg);

	//reg = 0;
	//transeiver.readRegister(RPD, &reg, 1);
	//printf("RPD: %x\n", reg);

	uint8_t reg_vals[6] = {0,0,0,0,0,0};
	transeiver.readRegister(RX_ADDR_P0, reg_vals, 5);
	printf(":RX_ADDR_P0: %s\n", reg_vals);

	transeiver.readRegister(RX_ADDR_P1, reg_vals, 5);
	printf(":RX_ADDR_P1: %s\n", reg_vals);

	reg = 0;
	transeiver.readRegister(RX_ADDR_P2, &reg, 1);
	printf(":RX_ADDR_P2: %x\n", reg);

	reg = 0;
	transeiver.readRegister(RX_ADDR_P3, &reg, 1);
	printf(":RX_ADDR_P3: %x\n", reg);

	reg = 0;
	transeiver.readRegister(RX_ADDR_P4, &reg, 1);
	printf(":RX_ADDR_P4: %x\n", reg);

	reg = 0;
	transeiver.readRegister(RX_ADDR_P5, &reg, 1);
	printf(":RX_ADDR_P5: %x\n", reg);

	transeiver.readRegister(TX_ADDR, reg_vals, 5);
	printf(":TX_ADDR: %s\n", reg_vals);

	reg = 0;
	transeiver.readRegister(RX_PW_P0, &reg, 1);
	printf(":RX_PW_P0: %x\n", reg);

	reg = 0;
	transeiver.readRegister(RX_PW_P1, &reg, 1);
	printf(":RX_PW_P1: %x\n", reg);

	reg = 0;
	transeiver.readRegister(RX_PW_P2, &reg, 1);
	printf(":RX_PW_P2: %x\n", reg);

	reg = 0;
	transeiver.readRegister(RX_PW_P3, &reg, 1);
	printf(":RX_PW_P3: %x\n", reg);

	reg = 0;
	transeiver.readRegister(RX_PW_P4, &reg, 1);
	printf(":RX_PW_P4: %x\n", reg);

	reg = 0;
	transeiver.readRegister(RX_PW_P5, &reg, 1);
	printf(":RX_PW_P5: %x\n", reg);

	reg = 0;
	transeiver.readRegister(FIFO_STATUS, &reg, 1);
	printf(":FIFO_STATUS: %x\n", reg);

	reg = 0;
	transeiver.readRegister(DYNPD, &reg, 1);
	printf(":DYNPD: %x\n", reg);
}

void process_uart_input(Nrf24 &transeiver, uint8_t * data_buffer){
	uint8_t pipe = 0;
	switch(data_buffer[0]){
		case 0: {
				  transeiver.send(data_buffer + 1); //make a macro to shift
				  while(transeiver.isSending())
					;
				} 
				break;
			
		case 1: transeiver.set_TX_address(data_buffer + 1);
				break;
				  
		case 2: pipe = data_buffer[1] - '0';
				transeiver.set_RX_address(data_buffer + 2, pipe);	
				break;
				  
		case 3: print_TX_address(transeiver);
				break;
				  
		case 4: pipe = data_buffer[1] - '0';
				print_RX_address(transeiver, pipe);
				break;
				  
		case 5: transeiver.setSuccessMode(!transeiver.isSuccessMode());
				break;
				
		case 6: { //get success mode
				    printf("STATE:");
				    USART_Transmit(transeiver.isSuccessMode() + '0');
				    USART_Transmit('\n');
				}
				break;
				
		case 7: PORTD ^= 1 << 5;    //getting the state of whether a port is on would be cool, this is where stron designing of the c code will come on
				break;
		case 8: //in python program this is for discover mode this is not meant to be implemented here
				break;
		case 9: // in python program this is for finding mode, again not to be implemented
				break; // will add a polling mode I think a separate pipe should be dedicated for that
			  
		default:
		        printf("INVALID STATE\n");
			
	}
}
void process_recieved(Nrf24 &transeiver, uint8_t * receive_buffer){
	static uint8_t success[32] = "<<<success>>>";
	switch(receive_buffer[0]){
		case '0': PORTD ^= 1 << 5;
				  break;
		case '1': transeiver.setSuccessMode(!transeiver.isSuccessMode());
		          break;
		case '2': //send to other node propogation
				  break;
		default :
			      break; //dummy statement need to make a new return statement
	}
	if(transeiver.isSuccessMode()){
		if(is_success(receive_buffer, success)){
			printf("SUCCESS:%s\n",success);
		}else{
			printf("RECEIVED:%s\n",receive_buffer); //bytes 0-9 need to be removed by program
			
			//for(uint8_t i = 0; i < 5; i++){
			//	success[13 + i] = rx_address[1][i]; //dummy address 1
			//}
			//success[18] = (PIND && (1 << 5)) + 48; //move this feature somewhere else
			//success[19] = 0;
			transeiver.send(success);
			
		}
	}
	else{
		printf("RECEIVED:%s\n",receive_buffer);
	}
}


uint8_t is_success(uint8_t * receive, uint8_t * success){
	uint8_t i;
	for(i = 0; i < 13; i++){
		if(receive[i] != success[i]){
			return FALSE;
		}
	}
	return TRUE;
}

void print_RX_address(Nrf24 &transeiver, uint8_t pipe){
	uint8_t * buffer = transeiver.get_RX_address(pipe);
	printf("STATE:");
	for(uint8_t i = 0; i < 5; i++){
		USART_Transmit(buffer[i]);
	}
	USART_Transmit('\n');
}

void print_TX_address(Nrf24 &transeiver){
	uint8_t * buffer = transeiver.get_TX_address();
	printf("STATE:");
	for(uint8_t i = 0; i < 5; i++){
		USART_Transmit(buffer[i]);
	}
	USART_Transmit('\n');
}



