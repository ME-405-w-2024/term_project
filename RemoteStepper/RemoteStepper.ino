// @file RemoteStepper.ino

#include <Wire.h>
#include "StepperFunctions.h"
#include "TimerFunctions.h"

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


bool receive_flag = false;


StepperDriver stepper0;


int16_t requested_pivot_target_deg = 0;
uint32_t requested_acceleration = 0;
uint32_t requested_deceleration = 0;
uint32_t requested_rotation_speed = 0;


int posState = 0;
int step1PosTarget = 360;

int currentAcccel = 0;
int currentDecel = 0;
int currentSpeed = 0;

void setup() {
  Serial.begin(230400);

  Wire.begin(0x69);
  Wire.setClock(400000);

  Wire.onRequest(request_handler);

  Wire.onReceive(receive_handler);

  timer1Setup();
  timer1Enable();

  //(int microsteps, int stepPerRev, int stepPin, int dirPin, int M1, int M2, int M3, int enablePin)
  stepper0.setupStepper(1, 200, 6, 5, 11, 10, 9, 12);


  for (int i = 2; i <=  20; i++) {
    pinMode(i, OUTPUT);
  }

  digitalWrite(7,HIGH);
  digitalWrite(8,HIGH);

  //timer0Setup();
  //TIMER0_DISABLE();

  //100000
  stepper0.setAcceleration(50000);
  stepper0.setDeceleration(50000);

  //setArmRotation(500, 360);

  stepper0.enableStepper();
}

void loop() {

  if (stepper0.getState() == 0){
    stepper0.disableStepper();

    if(receive_flag == true){

      receive_flag = false;
      stepper0.setAcceleration(requested_acceleration);
      stepper0.setDeceleration(requested_deceleration);
      stepper0.changePos(requested_pivot_target_deg,requested_rotation_speed);
      nextDelayTicks = stepper0.calculateNextStep();
      start_timer();
      stepper0.enableStepper();

    }

  } else {
    stepper0.enableStepper();
  }

}

void start_timer(){
  TCNT1 = 0;
  OCR1A = 100;
  timer1Enable();
}


void request_handler(){

}

void receive_handler(int bytes){
  

  Serial.print("Received data length: ");
  Serial.println(bytes);

  if(bytes == 8){

    receive_flag = true;
    
    while(Wire.available()){
      requested_pivot_target_deg =  (int16_t) (Wire.read()<<8) + (Wire.read()); 
      requested_rotation_speed = ((uint32_t) (Wire.read()<<8) + (Wire.read())) * 10;
      requested_acceleration = ((uint32_t) (Wire.read()<<8) + (Wire.read())) * 10;
      requested_deceleration = ((uint32_t) (Wire.read()<<8) + (Wire.read())) * 10;
    }

  }

}

//ISR overhead of about 8us
ISR(TIMER1_COMPA_vect) {

  cli(); //Mask interrupt

  // DDRDstate = DDRD;
  // PORTDstate = PORTD;
  // DDRBstate = DDRB;
  // PORTBstate = PORTB;
  // DDRCstate = DDRC;
  // PORTCstate = PORTC;

  do{

  OCR1A = 65535; //set compare to max
  TCNT1 = 0; //Reset timer counter

  if(stepper0.getState() != 0){

    stepper0.fullStep();//Step

  }

  sei(); //unmask interrupt

  

  nextActionTicks = stepper0.calculateNextStep(); //Get ticks to next step

  // Serial.println(nextActionTicks);

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


  // DDRD = DDRDstate;
  // PORTD = PORTDstate;
  // DDRB = DDRBstate;
  // PORTB = PORTBstate;
  // DDRC = DDRCstate;
  // PORTC = PORTCstate;

  sei(); //unmask interrupt
}






