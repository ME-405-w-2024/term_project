// @file TimerFunctions.cpp

#include "TimerFunctions.h"

uint8_t timer0Tick = 0;
uint8_t timer0LastTick = 0;

void timer0Setup(){

  cli();//stop interrupts

  //set timer0 interrupt at 1MHz for a 1us tick timer
  TCCR0A = 0;// set entire TCCR2A register to 0
  TCCR0B = 0;// same for TCCR2B
  TCNT0  = 0;//initialize counter value to 0
  
  // compare match register = [16,000,000 / (prescaler * freq(hz)) ] -1
  OCR0A = 159;  //(must be <256)
  
  // turn on CTC mode
  TCCR0A |= (1 << WGM01);
  
  // Set CS01 and CS00 bits for 256 prescaler
  TCCR0B |= (0 << CS02) | (0 << CS01) | (1 << CS00);  
   
  // enable timer compare interrupt
  TIMER0_ENABLE();

  sei();//allow interrupts
  
}

// void incrementTick(){
//   timer0Tick++;
// }

// void resetTick(){
//   timer0LastTick = timer0Tick;
//   timer0Tick = 0;
// }

// uint8_t returnLastTick(){
//   return timer0LastTick;
// }

void timer1Setup(){

  cli();//stop interrupts

  TCCR1A = 0;// set entire TCCR1A register to 0
  TCCR1B = 0;// same for TCCR1B
  TCNT1  = 0;//initialize counter value to 0
  
  OCR1A = 65535;//(must be <65536)
  
  // turn on CTC mode
  TCCR1B |= (1 << WGM12);
  
  // Set CS10 and CS12 bits for 8 prescaler
  TCCR1B |= (0 << CS12) | (1 << CS11) | (0 << CS10);  
  
  // enable timer compare interrupt
  TIMSK1 |= (1 << OCIE1A);

  sei();//allow interrupts
  
}

// void timer0ChangeFrequency(int frequencyHZ, int preScaler){
//   int newFreqVal = (long)16000000 / ((long)preScaler * frequencyHZ) - 1;
//   TCNT0  = 0;
//   OCR0A = newFreqVal;
// }

void timer1ChangeFrequency(long frequencyHZ, int preScaler){

  timer1Disable();

  TCCR1B &= 0b11111000;//Reset prescaler registers

  switch(preScaler){

    case 1:
      TCCR1B |= (0 << CS12) | (0 << CS11) | (1 << CS10); 
      break;

    case 8:
      TCCR1B |= (0 << CS12) | (1 << CS11) | (0 << CS10); 
      break;

    case 64:
      TCCR1B |= (0 << CS12) | (1 << CS11) | (1 << CS10); 
      break;

    case 256:
      TCCR1B |= (1 << CS12) | (0 << CS11) | (0 << CS10); 
      break;

    case 1024:
      TCCR1B |= (1 << CS12) | (0 << CS11) | (1 << CS10); 
      break;

    default:
      TCCR1B |= (0 << CS12) | (0 << CS11) | (1 << CS10); 
      break;
  }

  long newFreqVal = (long)16000000 / ((long)preScaler * frequencyHZ) - 1;
  TCNT1  = 0;
  OCR1A = newFreqVal;

  timer1Enable();
}

void timer1UpdateFrequency(long frequencyHZ, int preScaler){
  long newFreqVal = (long)16000000 / ((long)preScaler * frequencyHZ) - 1;
  OCR1A = newFreqVal;
}

void timer1Disable(){
  TIMSK1 = 0;
}

inline void timer1Enable(){
  TIMSK1 |= (1 << OCIE1A);
}
