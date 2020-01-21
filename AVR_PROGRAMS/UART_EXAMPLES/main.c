/*
 * Demonstration on how to redirect stdio to UART. 
 *
 * http://appelsiini.net/2011/simple-usart-with-avr-libc
 *
 * To compile and upload run: make clean; make; make program;
 * Connect to serial with: screen /dev/tty.usbserial-*
 *
 * Copyright 2011 Mika Tuupola
 *
 * Licensed under the MIT license:
 *   http://www.opensource.org/licenses/mit-license.php
 *
 */
 
#include <stdio.h>
#include <stdlib.h>
#include "main.h"
#include "../UART/uart.h"

int main(void) {    

    uart_init();
    stdout = &uart_output;
    stdin  = &uart_input;
    int c;
    //char * input = (char *)malloc(100);
    while(1) {
        puts("Hello world!\n");
       // scanf("%c%*c", input);
       // scanf("%99[0-9a-zA-Z ]", input);
       // printf("You wrote %s\n", input);
	//	scanf("%c%*c", input);
    }
        
    return 0;
}
