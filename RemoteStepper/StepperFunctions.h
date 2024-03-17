// @file StepperFunctions.h

#ifndef STEPPER_FUNC_H
#define STEPPER_FUNC_H

#include<Arduino.h>
#include "TimerFunctions.h"

//#define DEBUG

struct StepperParam{

	int microSteps;
    int pulsesPerRev;
    int stepperDirection;
    int stepperStepPin;
    int stepperDirPin;
    int stepperM1;
    int stepperM2;
    int stepperM3;
    int stepperEnablePin;
    int acceleration;
    int deceleration;


};

enum stepperStates {STOP, ACCELERATE, DECELERATE, CRUISE, ERROR};

class StepperDriver{
	private:


		#define PRESCALER 8
		#define SYSTEM_CLOCK 16e+6
		#define TIMER_CLOCK SYSTEM_CLOCK / PRESCALER

		int microSteps;
	    int stepsPerRev;
	    int stepperDirection;
	    int stepperStepPin;
	    int stepperDirPin;
	    int stepperM1;
	    int stepperM2;
	    int stepperM3;
	    int stepperEnablePin;

	    //Speed variables
	    long targetSpeed; //uSteps/s
	    long currentSpeed;
	    long accelVal; // uSteps/s^2
	    long decelVal; // uSteps/s^2  




	    //Position variables
	    long totalSteps;		// Current position in steps
	    long currentSteps;		// Current position in move
	    long posDelta;
	    long targetPulses;		// uSteps
	    long remainingSteps;	// to complete the current move (absolute value)
    	long accelSteps;		// steps to reach cruising (max) rpm
    	long decelSteps;		// steps needed to come to a full stop
    	long decelStartStep;	// step count at which to start decelerating
    	long currentSpeedPulse;	// step pulse duration (microseconds)
    	long pulseCalcRemainder;
    	long targetSpeedPulse;	// step pulse duration for constant speed section (max rpm)

	    //States
	    stepperStates currentState;

	    //Constants
	    static const int MIN_SPEED = 50;
	    static const int MAX_SPEED = 300;

	public:
		StepperDriver();
		/*!
		Stepper driver setup function
			@param microsteps Current microstepping mode in 1/microsteps
		*/
		void setupStepper(int microsteps, int stepPerRev, int stepPin, int dirPin, int M1, int M2, int M3, int enablePin);
		void setStepperSpeed(int speed);
		void updateStepperSpeed(int speed);
		int pulsesPerSecond(int speed);
		int stepMicros(int speed);
		void enableStepper();
		void disableStepper();
		void dirSetCW();
		void dirSetCCW();
		bool isDone();
		void setPos(long posDegree, int speed);
		void changePos(long posDegree, int speed);
		long getCurrentPosition();
		void resetPosition();
		void setBrake();
		void fullStep();
		void incrementPos();
		int getDir();
		stepperStates getState();
    	void setAcceleration(long accelVal);
    	void setDeceleration(long decelVal);
    	long getAcceleration();
    	long getDeceleration();
    	void calculateMoveProfile();
    	int getAccelSteps();
    	int getDecelSteps();
    	long calculateNextStep();
    	long getRemainingSteps();
    	long getTimeToNext();


};



#endif