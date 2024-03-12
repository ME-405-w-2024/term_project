#ifndef STEPPER_MAN_H
#define STEPPER_MAN_H

#include<Arduino.h>
#include "StepperFunctions.h"
#include "TimerFunctions.h"

//#define STEPMANDEBUG

enum managerStates {WAITING, STEPPING};

class StepperManager{
	private:
		//std::vector<StepperDriver> stepVec = {step0,step1};

		StepperDriver *step0, *step1;
		long timeDelta = 0;
		long nextStepTime[2] = {0,0};
		int currentStepper = -1;
		long shortestTime = INT8_MAX;
		managerStates currentState = WAITING;


	public:
		void init(StepperDriver* stepper0, StepperDriver* stepper1);
		StepperDriver* getStepperObj(int stepperNum);
		void setTimeDelta(long newTimeDelta);
		long getNextTime();
		void stepNext();
		int getCurrentStepper();
		void setPos(int stepperNum, long position, int speed);
		void changePos(int stepperNum, long position, int speed);
		int getState();
};



#endif