#include <stdio.h>
#include "../UART/uart.h"
#include "../SSD1306_C/Files/SSD1306.h"
#include "../SSD1306_C/Files/Font5x8.h"


int main(void)
{	
	GLCD_Setup();
	GLCD_SetFont(Font5x8, 5, 8, GLCD_Overwrite);

	GLCD_GotoXY(0, 0);
	GLCD_PrintString("Testing");

	GLCD_Render();
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
