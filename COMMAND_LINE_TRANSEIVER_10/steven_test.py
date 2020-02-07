void setup() {

Serial.begin(9600);  #set baud rate
Serial.println("Ready");  #print "Ready"

}

void loop() {

char inByte = ' ';
if(Serial.available()) { #only send data back if data has been sent

char inByte = Serial.read(); # read incoming data
Serial.println(inByte); # send data back in new line so its not all one long line

}

delay(100); # delay for 1/10 of a second
}