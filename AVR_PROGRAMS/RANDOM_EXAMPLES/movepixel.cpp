#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>
#include "../SSD1306/Framebuffer.h"

void delay(uint8_t time);

int main(){
	Framebuffer fb;
	char * text = (char *) malloc(27);
	for(int i = 0; i < 26; i++){
		text[i] = 'A' + i;
	}
	text[26] = '\0';
	return 0;
}



