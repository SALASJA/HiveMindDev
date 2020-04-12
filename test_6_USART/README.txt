This folder contains the test for
atmega328p/arduino nano/uno serial port
communication

in other words, arduino to program

The USART code here is compatible with any language
that can read serial ports

BAUDRATE is 9600

if on MAC or LINUX use "ls /dev/*" in terminal app to find port
hint->"Try disconnecting and connecting, see what
       disappears and shows"

One can use AVR crosspack tools to compile and load program
which I have a link of tutorial here
https://www.linkedin.com/pulse/introduction-avr-c-programming-macos-finally-attiny85-jorge-salas/?trackingId=ZUBziTtZSbuvwqTwPRXbvw%3D%3D

when installed just "bash programmer.sh"

Linux might be similar with AVR crosspack

if on Windows PC you must use Atmel Studio

if using Arduino IDE, make sure to PASTE the code
of the .ino file into a new file made in the IDE,
this sets up a folder in the Arduino folder in Documents.
In addition, make sure to copy and paste the UTIL
folder into the libraries folder thats within the Arduino folder.