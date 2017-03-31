#include <Arduino.h>
#include <Servo.h>

Servo myservo;  // create servo object to control a servo
int pos = 0;    // variable to store the servo position
char receivedChar;

void setup() {
  Serial.begin(9600);
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
}

void loop() {
  if (Serial.available() > 0) {
    receivedChar = Serial.read();
    switch(receivedChar) {
      case 'L':
        myservo.write(0);
      break;
      case 'U':
        myservo.write(90);
      break;
      case 'R':
        myservo.write(180);
      break;
    }
  }
}
