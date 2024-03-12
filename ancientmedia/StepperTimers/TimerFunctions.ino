void timer0Setup(){

  cli();//stop interrupts

  //set timer0 interrupt at 1kHz
  TCCR0A = 0;// set entire TCCR2A register to 0
  TCCR0B = 0;// same for TCCR2B
  TCNT0  = 0;//initialize counter value to 0
  
  // set compare match register for 500Hz increments
  // compare match register = [16,000,000 / (prescaler * freq(hz)) ] -1
  OCR0A = 124;  //(must be <256)
  
  // turn on CTC mode
  TCCR0A |= (1 << WGM01);
  
  // Set CS01 and CS00 bits for 256 prescaler
  TCCR0B |= (1 << CS02) | (0 << CS01) | (0 << CS00);  
   
  // enable timer compare interrupt
  TIMSK0 |= (1 << OCIE0A);


  sei();//allow interrupts
  
}


void timer1Setup(){

  cli();//stop interrupts

  //set timer1 interrupt at 1Hz
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


void timer0ChangeFrequency(int frequencyHZ, int preScaler){
  int newFreqVal = (long)16000000 / ((long)preScaler * frequencyHZ) - 1;
  TCNT0  = 0;
  OCR0A = newFreqVal;
}

void timer1ChangeFrequency(int frequencyHZ, int preScaler){
  int newFreqVal = (long)16000000 / ((long)preScaler * frequencyHZ) - 1;
  TCNT1  = 0;
  OCR1A = newFreqVal;
}

void timer1UpdateFrequency(int frequencyHZ, int preScaler){
  int newFreqVal = (long)16000000 / ((long)preScaler * frequencyHZ) - 1;
  OCR1A = newFreqVal;
}

void timer1Disable(){
  TIMSK1 = 0;
}

void timer1Enable(){
  TIMSK1 |= (1 << OCIE1A);
}
