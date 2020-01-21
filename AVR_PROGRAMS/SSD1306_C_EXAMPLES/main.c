#include <stdio.h>
#include <stdlib.h>
#include "../UART/uart.h"
#include "../SSD1306_C/Files/SSD1306.h"
#include "../SSD1306_C/Files/Font5x8.h"
///Users/jorgesalas/Documents/"ANSI C"/AVR_PROGRAMS/SSD1306_C_EXAMPLES


int main(void)
{	
	GLCD_Setup();
	GLCD_SetFont(Font5x8, 5, 8, GLCD_Overwrite);

	GLCD_GotoXY(0, 0);
    uart_init();
    stdout = &uart_output;
    stdin  = &uart_input;
    int c;
    char * input = (char *)malloc(100);
    while(1) {
        puts("Hello world!\n");
        scanf("%c%*c", input);
        scanf("%99[0-9a-zA-Z ]", input);
        GLCD_Clear();
        drawText(input, 0,0);
        printf("You wrote %s\n", input);
		//scanf("%c%*c", input);
		GLCD_Render();
    }
	//GLCD_PrintString("Testing");
	
	/*
    while (1 == 1)
    {
		GLCD_ScrollLeft(0, 0x0F);
		_delay_ms(1000);
		GLCD_ScrollRight(0, 0x0F);
		_delay_ms(1000);
		GLCD_ScrollDiagonalLeft(0, 0x0F);
		_delay_ms(1000);
		GLCD_ScrollDiagonalRight(0, 0x0F);
		_delay_ms(1000);
		GLCD_ScrollStop();
		_delay_ms(1000);
	}*/

	return 0;
}
