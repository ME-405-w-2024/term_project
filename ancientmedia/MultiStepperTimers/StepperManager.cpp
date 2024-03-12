#include "StepperManager.h"


void StepperManager::init(StepperDriver* stepper0, StepperDriver* stepper1){
  step0 = stepper0;
  step1 = stepper1;
  TCNT1 = 0;
  OCR1A = 100;
  timer1Enable();
}

StepperDriver* StepperManager::getStepperObj(int stepperNum){
  switch(stepperNum){
    case 0:
      return step0;
    break;

    case 1:
      return step1;
    break;
  }

}

int StepperManager::getCurrentStepper(){
  return currentStepper;
}


int StepperManager::getState(){
  return currentState;
}


void StepperManager::setTimeDelta(long newTimeDelta){
  //Set the new time delta to base calculations off of
  timeDelta = newTimeDelta;
}



long StepperManager::getNextTime(){

    if (getStepperObj(0)->getState() == 0 && getStepperObj(0)->getState() == 0){
      currentState = WAITING;
      return 1000;
    }

    currentState = STEPPING;

    int arraySize = sizeof(nextStepTime)/sizeof(nextStepTime[0]);

    //Subtract time delta from all stepper times

    for (int i = arraySize - 1; i >= 0; i--){

      if((nextStepTime[i] - timeDelta) > 0){
        nextStepTime[i] -= timeDelta;
      } else if (nextStepTime[i] != -1) {
        nextStepTime[i] = 0;
      }
      

    }




      #ifdef STEPMANDEBUG
      Serial.print("timeDelta: ");
      Serial.println(timeDelta);

      Serial.print("getState0: ");
      Serial.println(getStepperObj(0)->getState());

      Serial.print("getState1: ");
      Serial.println(getStepperObj(1)->getState());

      Serial.print("currentStepper ");
      Serial.println(currentStepper);
      #endif 

    //If we are currently on a stepper, that means it just stepped, and it needs to be recalculated
    if(currentStepper >= 0){

        //Only calculate if stepper is not stopped
        if(getStepperObj(currentStepper)->getState() != 0) {
          nextStepTime[currentStepper] = (long) getStepperObj(currentStepper)->calculateNextStep();
          // Serial.print("nextStepTime[currentStepper] : ");
          // Serial.println(nextStepTime[currentStepper] );
        } else {
          nextStepTime[currentStepper] = -1;
        }


    
    //if no stepper just stepped (probably denoted by -1) then calculate all
    } else {

      for (int i = arraySize - 1; i >= 0; i--){
        //Only calculate if stepper is not stopped

        if(getStepperObj(i)->getState() != 0) {
          nextStepTime[i] = getStepperObj(i)->calculateNextStep();
        } else {
          nextStepTime[i] = -1;
        
        }

      }
    }




    shortestTime = 65535;
    //set current stepper to the smallest delay time that is greater than 0
    for (int i = arraySize - 1; i >= 0; i--){
        //Find the shortest time and corresponding stepper

        //#ifdef STEPMANDEBUG
        // Serial.print("nextStepTime[");
        // Serial.print(i);
        // Serial.print("]: ");
        // Serial.println(nextStepTime[i]);
       //#endif

      if(nextStepTime[i] < shortestTime && nextStepTime[i] > -1) {
        shortestTime = nextStepTime[i];
        currentStepper = i;
      }

    }



    //Serial.print("shortestTime: ");
    //Serial.println(shortestTime);
    //Serial.println();
    return shortestTime;
}

void StepperManager::setPos(int stepperNum, long position, int speed){
  getStepperObj(stepperNum)->setPos(position,speed);
  nextStepTime[stepperNum] = getStepperObj(stepperNum)->getTimeToNext();
  timer1Enable();
}

void StepperManager::changePos(int stepperNum, long position, int speed){
  getStepperObj(stepperNum)->changePos(position,speed);
  nextStepTime[stepperNum] = getStepperObj(stepperNum)->getTimeToNext();
  timer1Enable();
}

void StepperManager::stepNext(){

  //Step the current stepper
  getStepperObj(currentStepper)->fullStep();

}