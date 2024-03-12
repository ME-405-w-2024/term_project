#include <Wire.h>

int currentState = 0;
int lastState = 0;

int potValScaled = 0;
int lastVal = 0;
int speedSet = 300;
int inputPos = 0;

void setup() {
  Serial.begin(230400);

  for (int i = 2; i <= 7; i++) {
    pinMode(i, OUTPUT);
  }

  timer1Setup();

  

  //setupStepper(int microsteps, int stepPerRev, int stepPin, int dirPin, int M1, int M2, int M3, int enablePin)
  setupStepper(4, 200, 5, 6, 2, 3, 4, 7);
  setBrake();

  //setStepperSpeed(100 * 3);

  enableStepper();
  //disableStepper();
  resetPulsesPos();
  //dirSetCW();
  //setPos(180*3,200);


  Wire.begin(8);                // join i2c bus with address #8
 // Wire.onReceive(receiveEvent); // register event

}

void loop() {

  potValScaled = map(analogRead(A0),0,1024,50,400);
//  potValScaled = map(analogRead(A0),0,1024,-135*3,135*3);
//
//  if(abs(potValScaled-lastVal)>3){
//    
//    setPos(potValScaled, 300);
//    
//  }

//  if(inputPos<=100){
//    setPos(inputPos*3*2, speedSet);
//    lastVal = inputPos;
//  }
  
  
  
  delay (5);

  if (isDone()) {
    currentState++;
    //Serial.println(currentState);
  }

  if (lastState != currentState) {
    switch (currentState) {
      case 0:
        setPos(180 * 3, potValScaled);
        break;
      case 1:
        setPos(0 * 3, potValScaled);
        break;
//      case 2:
//        setPos(1080 * 3, 250);
//        break;
//      case 3:
//        setPos(0 * 3, 350);
//        break;
      default:
        //disableStepper();
        //delay(5000);
        currentState = -1;
        //enableStepper();
        break;
    }
    lastState = currentState;
  }

}


// function that executes whenever data is received from master
// this function is registered as an event, see setup()
void receiveEvent(int howMany) {
  
  int x = Wire.read();    // receive byte as an integer

  

  switch(x){
    case 10:
      inputPos = Wire.read();
      Serial.println(inputPos);
      break;
    case 20:
      speedSet = Wire.read();
      break;
    default:
      break;
  }
}
