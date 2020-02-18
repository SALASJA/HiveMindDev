#include <avr/io.h>
#include <util/delay.h>

#ifdef __cplusplus
extern "C"{
#endif
#include "UART/uart.h"
#ifdef __cplusplus
}
#endif


int main(){    // forces to return int when in CPP
	USART_Init();
	while(1){
 		printf("Hello world\n");
 		_delay_ms(10);
 	}
 	return 0;
}