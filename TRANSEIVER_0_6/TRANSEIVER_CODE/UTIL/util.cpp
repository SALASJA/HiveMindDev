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
				  copy(transeiver.RX_ADDR_P_VAL[0], data_buffer + 29);
				  //for(int i = 29; i < 32; i++){
				  //	USART_Transmit(data_buffer[i]);
				  //}
				  //USART_Transmit('\n');
				  transeiver.send(data_buffer + 1); //make a macro to shift
				  while(transeiver.isSending())
					;
				} 
				break;
			
		case 1: transeiver.set_TX_address(data_buffer + 1);
				break;
				  
		case 2: pipe = data_buffer[1];
				transeiver.set_RX_address(data_buffer + 2, pipe);	
				break;
				  
		case 3: print_TX_address(transeiver);
				break;
				  
		case 4: pipe = data_buffer[1];
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
	static uint8_t address[32] = "3";
	uint8_t sent_address = FALSE;
	uint8_t receive_address = FALSE;
	uint8_t on = FALSE;
	switch(receive_buffer[0]){
		case '0': PORTD ^= 1 << 5;
				  break;
		case '1': transeiver.setSuccessMode(!transeiver.isSuccessMode());
		          break;
		case '2': if(!on){
				  	PORTD ^= 1 << 5;
				  	on = TRUE;
				  }
				  transeiver.set_TX_address(receive_buffer + 1);
		          copy(transeiver.RX_ADDR_P_VAL[0], address + 1);
		          transeiver.send(address);
		          transeiver.set_TX_address(transeiver.TX_ADDR_VAL);
		          sent_address = TRUE;
				  break;
		case '3': print_address(receive_buffer + 1);
				  receive_address = TRUE;
				  break;
		default :
			      break; //dummy statement need to make a new return statement
	}
	if(!sent_address && !receive_address){
		if(transeiver.isSuccessMode()){
			if(is_success(receive_buffer, success)){
				//printf("caught\n");
				print_success(success);
			}else{
				print_receive(receive_buffer);
				transeiver.set_TX_address(receive_buffer + 28);
				copy(receive_buffer + 28, success + 13); //16
				//print_receive(success);
				transeiver.send(success);
				transeiver.set_TX_address(transeiver.TX_ADDR_VAL);
			}
		}
		else{
			//printf("success off\n");
			print_receive(receive_buffer);
		}
	}
}

void copy(uint8_t * buffer_1, uint8_t * buffer_2){
	for(int i = 0; i < 3; i++){
		buffer_2[i] = buffer_1[i];
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


void print_success(uint8_t * buffer){
	printf("SUCCESS:");
	for(uint8_t i = 0; i < 16; i++){
		USART_Transmit(buffer[i]);
	}
	USART_Transmit('\n');
	
}

void print_receive(uint8_t * buffer){
	printf("RECEIVED:");
	for(uint8_t i = 0; buffer[i] != 0; i++){
		USART_Transmit(buffer[i]);
	}
	USART_Transmit('\n');
}

void print_address(uint8_t * address){
	printf("ADDRESS:");
	for(uint8_t i = 0; i < 3; i++){
		USART_Transmit(address[i]);
	}
	USART_Transmit('\n');
}

void print_RX_address(Nrf24 &transeiver, uint8_t pipe){
	uint8_t * buffer = transeiver.get_RX_address(pipe);
	uint8_t shift = 0;
	if(2 <= pipe && pipe <= 5){
		shift = 2;
	}
	printf("STATE:");
	for(uint8_t i = 0 + shift; i < 3 + shift; i++){
		USART_Transmit(buffer[i]);
	}
	USART_Transmit('\n');
}

void print_TX_address(Nrf24 &transeiver){
	uint8_t * buffer = transeiver.get_TX_address();
	printf("STATE:");
	for(uint8_t i = 0; i < 3; i++){
		USART_Transmit(buffer[i]);
	}
	USART_Transmit('\n');
}



