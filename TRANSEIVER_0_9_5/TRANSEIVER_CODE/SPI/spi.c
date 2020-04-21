#include "spi.h"
            
void standardSPIPinInit() {
	set_CE_Pin(DataDirectionRegister,CE_Pin); 
	set_CSN_Pin(DataDirectionRegister,CSN_Pin);
	set_SCK_Pin(DataDirectionRegister,SCK_Pin);
	set_MOSI_Pin(DataDirectionRegister,MOSI_Pin);
	set_MISO_Pin(DataDirectionRegister,MISO_Pin);
}

void set_CE(uint8_t state){
	if(state){
		set_HIGH(PinOnOffRegister,CE_Pin);
	}
	else{
		set_LOW(PinOnOffRegister,CE_Pin);
	}
}

void set_CSN(uint8_t state){
	if(state){
		set_HIGH(PinOnOffRegister,CSN_Pin);
	}
	else{
		set_LOW(PinOnOffRegister,CSN_Pin);
	}
}

void set_SCK(uint8_t state){
	if(state){
		set_HIGH(PinOnOffRegister,SCK_Pin);
	}
	else{
		set_LOW(PinOnOffRegister,SCK_Pin);
	}
}

void set_MOSI(uint8_t state){
	if(state){
		set_HIGH(PinOnOffRegister,MOSI_Pin);
	}
	else{
		set_LOW(PinOnOffRegister,MOSI_Pin);
	}
}

uint8_t get_MISO_State(){
	return get_Pin_State(PinStateRegister,MISO_Pin);
}



uint8_t spi_transfer(uint8_t byte_to_send)
{
    uint8_t i = 0;
    uint8_t bits_received = 0;    
    set_SCK(LOW);
    for(i = 0; i < 8; i++){
    
    	if(getBitL(byte_to_send, i)){ //getBitL access bit state at position L, where 0 is far left ex. getBitL(1010, 0) = 1 and getBitL(1010, 2) = 1
    		set_MOSI(HIGH);
    	}                    
		else{
			set_MOSI(LOW);
		}
					
        set_SCK(HIGH);        

		bits_received = bits_received << 1;
		if(get_MISO_State()){
			bits_received |= 0x01;
		}  //gets bit from miso by checking if its high and pushes it onto byte sized variable from right

        set_SCK(LOW);               

    }

    return bits_received;
}