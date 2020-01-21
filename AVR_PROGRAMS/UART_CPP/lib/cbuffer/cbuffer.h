/*
 *	CBuffer.h -- A Simple C++ Circular Buffer Implementation.
 *
 *	-> Author:		Théophile Gaudin
 *	-> Version:		1.0
 *	-> Date:		25.10.2016
 *
 * 
 * "THE BEER-WARE LICENSE" (Revision 42):
 * <theophile.gaudin@gmail.com> wrote this file. As long as you retain this notice you
 * can do whatever you want with this stuff. If we meet some day, and you think
 * this stuff is worth it, you can buy me a beer in return.
 *												Théophile Gaudin
 *
 *	-> Changelog
 *		25.10.16:	Initial commit.
 *
 *
 */


#ifndef CBUFFER_H
#define CBUFFER_H

#include <stdint.h>


template<typename type, int size>
class CBuffer {
	public:
		CBuffer(void) = default;
		bool write(type *data);
		bool read(type *data);
		bool is_full(void);
		bool is_empty(void);
	private:
		volatile type array[size];
		int head = 0;
		int tail = 0;
};



template<typename type, int size> 
bool CBuffer<type, size>::write(type *data) {
	if (is_full()) return false;
	head = (head + 1) % size;
	array[head] = *data;
	return true;	
}

template<typename type, int size>
bool CBuffer<type,size>::read(type *data) {
	if (is_empty()) return false;
	tail = (tail + 1) % size;
	*data = array[tail];	
	return true;
}	


template<typename type, int size>
bool CBuffer<type,size>::is_full(void) {
	if ((head + 1) % size == tail) return true;
	return false;
}

template<typename type, int size>
bool CBuffer<type,size>::is_empty(void) {
	if (head == tail) return true;
	return false;
}


#endif // CBUFFER_H
