#include <iostream>

#include "../cbuffer.h"


int main(void) {
	char ch;
	int value;
	bool result;

	CBuffer<int,10> buffer;			// Initialize a buffer of 10 integers


	while(1) {
		std::cout << "What do you want to do? [r]ead or [w]rite?" << std::endl;
		std::cin >> ch;
		switch(ch) {
			case 'w':
				std::cout << "Enter a value: ";
				std::cin >> value;
				result = buffer.write(&value);	
				if (result) {
					std::cout << "DONE!" << std::endl;
				} else {
					std::cout << "ERROR: Buffer full!" << std::endl;
				}
				break;
			case 'r':
				result = buffer.read(&value);
				if(result) {
					std::cout << "Value: " << value << std::endl;
				} else {
				   	std::cout << "ERROR: Buffer empty!" << std::endl;
				}
				break;
		}

	}
	return 0;
}
