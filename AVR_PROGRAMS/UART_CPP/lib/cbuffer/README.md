# CBuffer
A simple C++ circular buffer implementation designed to be used in Arduino/AVR related project. This implementation use templates to avoid dealing with memory allocation.
## Usage
#### Initialization
```c++
CBuffer<int,10> buffer;
```
#### Writing and reading data

```c++
buffer.write(10);

int value;
buffer.read(&value);
```
Both read and write methods return true if succesful and false if the buffer is full or empty.

#### Buffer status
```c++
buffer.is_full();
buffer.is_empty();
```
Both methods return a bool. I guess what they do is pretty self-explanatory! ;)

## Example
If you need more information, please take a look at the example.
