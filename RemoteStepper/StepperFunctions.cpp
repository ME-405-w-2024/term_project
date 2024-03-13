

#include "StepperFunctions.h"

  

    StepperDriver::StepperDriver() {
      currentState = ERROR;
    }


    void StepperDriver::setupStepper(int microsteps, int stepPerRev, int stepPin, int dirPin, int M1, int M2, int M3, int enablePin) {
      microSteps = microsteps;
      stepsPerRev = stepPerRev;
      stepperStepPin = stepPin;
      stepperDirPin = dirPin;
      stepperM1 = M1;
      stepperM2 = M2;
      stepperM3 = M3;
      stepperEnablePin = enablePin;

      disableStepper();

      currentState = STOP;

      int m1State = 0;
      int m2State = 0;
      int m3State = 0;

      switch (microsteps) {
        case 2:
          m1State = 1;
          break;

        case 4:
          m2State = 1;
          break;

        case 8:
          m1State = 1;
          m2State = 1;
          break;

        case 16:
          m1State = 1;
          m2State = 1;
          m3State = 1;
          break;
      }

      digitalWrite(stepperM1, m1State);
      digitalWrite(stepperM2, m2State);
      digitalWrite(stepperM3, m3State);

      
    }


    void StepperDriver::setStepperSpeed(int speed) {
      updateStepperSpeed(pulsesPerSecond(speed));
      timer1ChangeFrequency(pulsesPerSecond(speed) * 2, 8); //multipled by 2 because toggle
      timer1Enable();
    }

//    void setTargetSpeed(int RPM) {
//      targetSpeed = RPM;
//      targetDegPerSec = RPM * 6;
//      timer1Enable();
//      stopped = false;
//    }

    void StepperDriver::updateStepperSpeed(int speed) {
      targetSpeed = speed;
    }





    //Calculations
    int StepperDriver::pulsesPerSecond(int speed) {
      return ((long)speed * stepsPerRev * microSteps) / 360;
    }

    int StepperDriver::stepMicros(int speed) {
      return 1000000 / speed;
    }





    //Enable/Disable
    void StepperDriver::enableStepper() {
      digitalWrite(stepperEnablePin, 0);
    }

    void StepperDriver::disableStepper() {
      digitalWrite(stepperEnablePin, 1);
    }





    //Direction
    void StepperDriver::dirSetCW() {
      stepperDirection = 1;
      digitalWrite(stepperDirPin, HIGH);

      #ifdef DEBUG
      Serial.println("CW Direction");
      #endif
    }

    void StepperDriver::dirSetCCW() {
      stepperDirection = -1;
      digitalWrite(stepperDirPin, LOW);

      #ifdef DEBUG
      Serial.println("CCW Direction");
      #endif
    }

    int StepperDriver::getDir() {
      return stepperDirection;
    }





    //States
    stepperStates StepperDriver::getState(){
      return currentState;
    }






    //Positioning
    void StepperDriver::setPos(long posDegree, int speed) { //speed in deg/s

      timer1Disable();


      if(posDegree < getCurrentPosition()){
        dirSetCCW();   

      } else {
        dirSetCW();

      }

      posDelta = abs(getCurrentPosition() - posDegree);
      targetSpeed = pulsesPerSecond(speed); //outputs uSteps/s
      targetPulses = ((long)posDelta * stepsPerRev) / 360 * microSteps;

      calculateMoveProfile();

      //Set current state to acceleration
      currentState = ACCELERATE;

      enableStepper();

      #ifdef DEBUG
      Serial.print("currentPosition:");
      Serial.println(getCurrentPosition());
      Serial.print("posDelta:");
      Serial.println(posDelta);
      Serial.print("targetPulses:");
      Serial.println(targetPulses);
      Serial.print("Initial currentSpeedPulse: ");
      Serial.println(currentSpeedPulse);
      Serial.println();
      #endif



      //Set timer to delay and start timer
      // cli();
      // TCNT1 = 0;
      // OCR1A = currentSpeedPulse;
      // timer1Enable();
      // sei();
      

    }

    void StepperDriver::changePos(long posDegree, int speed) { //speed in deg/s

      timer1Disable();


      if(posDegree < 0){
        dirSetCCW();   

      } else {
        dirSetCW();

      }

      posDelta = abs(posDegree);
      targetSpeed = pulsesPerSecond(speed); //outputs uSteps/s
      targetPulses = ((long)posDelta * stepsPerRev) / 360 * microSteps;

      calculateMoveProfile();

      //Set current state to acceleration
      currentState = ACCELERATE;

      enableStepper();


      #ifdef DEBUG
      Serial.print("currentPosition:");
      Serial.println(getCurrentPosition());
      Serial.print("posDelta:");
      Serial.println(posDelta);
      Serial.print("targetPulses:");
      Serial.println(targetPulses);
      Serial.print("Initial currentSpeedPulse: ");
      Serial.println(currentSpeedPulse);
      Serial.println();
      #endif



      //Set timer to delay and start timer
      // cli();
      // TCNT1 = 0;
      // OCR1A = currentSpeedPulse;
      // timer1Enable();
      // sei();
      

    }

    long StepperDriver::getCurrentPosition() {
      return (totalSteps*360)/(stepsPerRev*microSteps);
    }

    void StepperDriver::resetPosition() {
      totalSteps = 0;
    }

    void StepperDriver::incrementPos(){
      totalSteps += stepperDirection;
    }






    //Stepping
    void StepperDriver::fullStep() {
      digitalWrite(stepperStepPin, HIGH);
      //PORTD = PORTD | 1 << (stepperStepPin);
      incrementPos();
      remainingSteps--;
      currentSteps++;
      digitalWrite(stepperStepPin, LOW);
      //PORTD = PORTD & 0 << (stepperStepPin);
    }

    void StepperDriver::setBrake() {
      if (currentState != STOP) {
        digitalWrite(stepperStepPin, LOW);
        currentState = STOP;
      }
      currentSpeedPulse = 65535;
      currentSpeed = 0;
      targetSpeed = 0;
    }





    void StepperDriver::setAcceleration(long accelDeg){ //input is deg/s^2
      accelVal = ((long)accelDeg*stepsPerRev*microSteps)/360; //output is uSteps/s^2
      #ifdef DEBUG
      Serial.print("accelVal: ");
      Serial.println(accelVal);
      #endif
    }

    void StepperDriver::setDeceleration(long decelDeg){
      decelVal = ((long)decelDeg*stepsPerRev*microSteps)/360;
    }

    long StepperDriver::getAcceleration(){
      return accelVal;
    }

    long StepperDriver::getDeceleration(){
      return decelVal;
    }

    void StepperDriver::calculateMoveProfile(){

        // speed is in [uSteps/s]
        // how many microsteps from 0 to target speed
        accelSteps = ( (long)targetSpeed * targetSpeed / ((long)2*accelVal) );
        // how many microsteps are needed from cruise speed to a full stop
        decelSteps = (long)accelSteps * accelVal / decelVal;

        if (targetPulses < accelSteps + decelSteps){
          // cannot reach max speed, will need to brake early
          accelSteps = (long)targetPulses * decelVal / ((long)accelVal + decelVal);
          decelSteps = (long)targetPulses - accelSteps;

        }

        decelStartStep = targetPulses - decelSteps;


        //Set remaining steps
        currentSteps = 0;
        remainingSteps = targetPulses;

        // Initial pulse (c0) including error correction factor 0.676 [us]
        currentSpeedPulse = -1 * (float) ((TIMER_CLOCK)*0.676) * sqrt(2.0/accelVal);

        pulseCalcRemainder = 0;

        
        // // Save cruise timing since we will no longer have the calculated target speed later
        targetSpeedPulse = TIMER_CLOCK / targetSpeed;

        // #ifdef DEBUG
        Serial.print("decelStartStep: ");
        Serial.println(decelStartStep);

        Serial.print("accelSteps: ");
        Serial.println(accelSteps);

        Serial.print("decelSteps: ");
        Serial.println(decelSteps);

        Serial.print("currentSpeedPulse: ");
        Serial.println(currentSpeedPulse);

        Serial.print("targetSpeedPulse: ");
        Serial.println(targetSpeedPulse);

        Serial.println();
        // #endif




    }

    long StepperDriver::calculateNextStep(){



      if (currentSteps >= decelStartStep && currentSteps < targetPulses){
        currentState = DECELERATE;

        currentSpeedPulse = (long)currentSpeedPulse - ( ((long)2 * currentSpeedPulse + pulseCalcRemainder) / ( ((long)-4 * remainingSteps) + 1) );
        pulseCalcRemainder = ((long)2 * currentSpeedPulse + pulseCalcRemainder) % ((long)-4 * remainingSteps + 1);


      } else if(currentSteps < accelSteps){
          currentState = ACCELERATE;

          currentSpeedPulse = (long)currentSpeedPulse - ( ((long)2 * currentSpeedPulse + pulseCalcRemainder) / ( ((long)4 * currentSteps) + 1) );
          pulseCalcRemainder = ((long)2 * currentSpeedPulse + pulseCalcRemainder) % ((long)-4 * currentSteps + 1);

      } else if (currentSteps < targetPulses){
        currentState = CRUISE;

        currentSpeedPulse = targetSpeedPulse;

        pulseCalcRemainder = 0;


      } else {

        currentState = STOP;
        pulseCalcRemainder = 0;
        currentSpeedPulse = 65535;
        setBrake();


      }


      return currentSpeedPulse;
    }

    long StepperDriver::getTimeToNext(){
      return currentSpeedPulse;
    }

    int StepperDriver::getAccelSteps(){
      return accelSteps;
    }

    int StepperDriver::getDecelSteps(){
      return decelSteps;
    }

    long StepperDriver::getRemainingSteps(){
      return remainingSteps;
    }










