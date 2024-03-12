
#include <Wire.h>
#include "StepperFunctions.h"
#include "TimerFunctions.h"
#include "StepperManager.h"

int currentState = 0;
int lastState = 0;

int potValScaled = 0;
int lastVal = 0;
int speedSet = 300;
int inputPos = 90*3;

int calcTicks = 0;
long delayTicks = 0;

long nextDelayTicks = 0;

byte DDRDstate = 0;
byte PORTDstate = 0;
byte DDRBstate = 0;
byte PORTBstate = 0;
byte DDRCstate = 0;
byte PORTCstate = 0;

long toop = 0;

long nextActionTicks = 0;
long interruptElapsedTicks = 0;


StepperDriver stepper0;
StepperDriver stepper1;

StepperManager steppers;

int posState = 0;
int step1PosTarget = 360;

int currentAcccel = 0;
int currentDecel = 0;
int currentSpeed = 0;

void setup() {
  Serial.begin(230400);

  timer1Setup();
  timer1Enable();

  //(int microsteps, int stepPerRev, int stepPin, int dirPin, int M1, int M2, int M3, int enablePin)
  stepper0.setupStepper(4, 200, 3, 2, 15, 16, 17, 20);
  stepper1.setupStepper(4, 200, 5, 4, 15, 16, 17, 20);


  steppers.init(&stepper0, &stepper1);

  for (int i = 2; i <=  20; i++) {
    pinMode(i, OUTPUT);
  }

  //timer0Setup();
  //TIMER0_DISABLE();



  stepper1.setAcceleration(5000);
  stepper1.setDeceleration(5000);
  stepper0.setAcceleration(5000);
  stepper0.setDeceleration(5000);

  //setArmRotation(500, 360);
  


}

void loop() {



  // if (stepper1.getState() == 0){

  //   step1PosTarget *= -1;
  //   steppers.setPos(1,step1PosTarget,500);
  //   steppers.setPos(0,step1PosTarget,500);
  // }

  // if (stepper0.getState() == 0){
  //   switch (posState){
  //     case 0:
  //       inputPos = 360;
  //       currentAcccel = 2000;
  //       currentDecel = 2000;
  //       currentSpeed = 500;
  //     break;


  //     case 1:
  //       inputPos = 0;
  //       currentAcccel = 1000;
  //       currentDecel = 1000;
  //       currentSpeed = 1000;
  //     break;


  //     case 2:
  //       inputPos = -360;
  //       currentAcccel = 10000;
  //       currentDecel = 10000;
  //       currentSpeed = 360;
  //     break;


  //     case 3:
  //       inputPos = 0;
  //       currentAcccel = 10000;
  //       currentDecel = 1000;
  //       currentSpeed = 500;

  //       posState = -1;
  //     break;


  //     default:
  //       posState = 0;
  //     break;
  //   }

   if (steppers.getState() == 0){
    switch (posState){
      case 0:
        setArmRotation(500, 90);
      break;


      case 1:
        setArmPivot(500, 180);
      break;

      case 2:
      delay(500);
        setArmPivot(500, -180);
      break;

      case 3:
        setArmRotation(500, -90);
      break;

      case 4:
        setArmPivot(500, 360);
      break;

      case 5:
        setArmRotation(500, -90);
      break;

      case 6:
        setArmPivot(500, 90);
      break;

      case 7:
        setArmPivot(500, -90);
      break;

      case 8:
        setArmPivot(500, -90);
      break;

      case 9:
        setArmPivot(500, 90);
      break;

      case 10:
        setArmRotation(500, 90);
      break;

      default:
        posState = 69;
      break;
    }

       posState++;
   }

  //while(stepper0.getState() != 0){

    // Serial.print("Step: ");
    // Serial.print(stepper0.getCurrentSteps());
    // Serial.print("  |  ");

    // Serial.print("State: ");
    // Serial.print(stepper0.getState());
    // Serial.print("  |  ");

    // Serial.print("Delay Ticks: ");
    // cli();
    // TCNT1 = 0;
    // delayTicks = stepper0.calculateNextStep();
    // calcTicks = TCNT1;
    // sei();

    // Serial.print(delayTicks);
    // Serial.print("  |  ");

    // Serial.print("Time to calculate: ");
    // Serial.print(TCNT1*50);
    // Serial.print("ns");

    // cli();
    // Serial.print("Step: ");
    // Serial.print(stepper0.getCurrentSteps());
    // Serial.print("  |  ");
    // Serial.print("Elapsed: ");
    // Serial.print(interruptElapsedTicks);
    // Serial.print("    Delay: ");
    // Serial.print(OCR1A);
    // Serial.print("    Next Action: ");
    // Serial.println(OCR1A+interruptElapsedTicks);
    // sei();

  //}

}

void setArmRotation(int speed, int degrees){



    steppers.changePos(0, - degrees*3 , speed);
    steppers.changePos(1, - degrees*3 , speed);

  
  
}

void setArmPivot(int speed, int degrees){

  steppers.changePos(0,  + degrees*3 , speed);
  steppers.changePos(1,  - degrees*3 , speed);
}


//ISR overhead of about 8us
ISR(TIMER1_COMPA_vect) {

  cli(); //Mask interrupt

  DDRDstate = DDRD;
  PORTDstate = PORTD;
  DDRBstate = DDRB;
  PORTBstate = PORTB;
  DDRCstate = DDRC;
  PORTCstate = PORTC;

  do{

  OCR1A = 65535; //set compare to max
  TCNT1 = 0; //Reset timer counter
  if(steppers.getState() == 1){

  steppers.stepNext();//Step

  }

  sei(); //unmask interrupt

  nextActionTicks = steppers.getNextTime(); //Get ticks to next step
  steppers.setTimeDelta(nextActionTicks); //Set new reference time for stepper manager

  cli(); //mask interrupt
  interruptElapsedTicks = TCNT1; //Get how many ticks have elapsed while in the interrupt
  TCNT1 = 0; //reset timer
  
  nextDelayTicks = nextActionTicks-interruptElapsedTicks; //set next interrupt taking into account how much time this one has taken

  if(nextDelayTicks > 16){//Take in account the 8 us overhead
    OCR1A = nextDelayTicks;
  } else {
      //Serial.println("Fuk");
      //Serial.println();
  }

    // Serial.print(nextActionTicks);
    // Serial.print(" - ");
    // Serial.print(interruptElapsedTicks);
    // Serial.print(" = ");
    // Serial.println(nextDelayTicks);
    // Serial.println();

  } while(nextDelayTicks < 16); //Repeat if there is not enough time for leaving the interrupt


  DDRD = DDRDstate;
  PORTD = PORTDstate;
  DDRB = DDRBstate;
  PORTB = PORTBstate;
  DDRC = DDRCstate;
  PORTC = PORTCstate;

  sei(); //unmask interrupt
}






