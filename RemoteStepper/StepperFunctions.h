// @file StepperFunctions.h

#ifndef STEPPER_FUNC_H
#define STEPPER_FUNC_H

#include<Arduino.h>
#include "TimerFunctions.h"

//#define DEBUG

/*!Struct containing the necessary attributes of a stepper controller
*/
struct StepperParam{
	
	//!Current microstepping mode in 1/microsteps
	int microSteps; 
	//!The number of physical steps per revolution of the stepper
    int pulsesPerRev; 
	//!Direction to move the stepper motor in
    int stepperDirection; 
	//!The pin number corresponding to the STEP pin on the DRV8825 for this motor
    int stepperStepPin; 
	//!The pin number corresponding to the DIR pin on the DRV8825 for this motor
    int stepperDirPin;
	//!The pin number corresponding to the M1 pin on the DRV8825 for this motor
    int stepperM1; 
	//!The pin number corresponding to the M2 pin on the DRV8825 for this motor
    int stepperM2; 
	//!The pin number corresponding to the M3 pin on the DRV8825 for this motor
    int stepperM3; 
	//!The pin number corresponding to the EN pin on the DRV8825 for this motor
    int stepperEnablePin; 
	//!The target acceleration for this motor in deg/sec^2
    int acceleration; 
	//!The target deceleration for this motor in deg/sec^2
    int deceleration; 


};

enum stepperStates {STOP, ACCELERATE, DECELERATE, CRUISE, ERROR};

/*!Contains functions to control a stepper motor using a DRV8825.
Enables step planning for target speed, position, accel, and decel values
*/
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
			@param stepPerRev The number of physical steps per revolution of the stepper
			@param stepPin The pin number corresponding to the STEP pin on the DRV8825
			@param dirPin The pin number corresponding to the DIR pin on the DRV8825
			@param M1 The pin number corresponding to the M1 pin on the DRV8825
			@param M2 The pin number corresponding to the M2 pin on the DRV8825
			@param M3 The pin number corresponding to the M3 pin on the DRV8825
			@param enablePin The pin number corresponding to the EN pin on the DRV8825
		*/
		void setupStepper(int microsteps, int stepPerRev, int stepPin, int dirPin, int M1, int M2, int M3, int enablePin);
		/*!
			Function to control stepper speed
			@param speed Speed in DEG/s to set the motor to
		*/
		void setStepperSpeed(int speed);
		/*!
			Function to update stepper speed
			@param speed Speed in DEG/s to update the motor to
		*/
		void updateStepperSpeed(int speed);
		/*!
			Function to get pulses per second from RPM
			@param speed Speed in DEG/s to convert
		*/
		int pulsesPerSecond(int speed);
		/*!
			Function to get microseconds per step
			@param speed Speed in STEP/sec
		*/
		int stepMicros(int speed);
		/*!
			Enables stepper driver
		*/
		void enableStepper();
		/*!
			Disables stepper driver
		*/
		void disableStepper();
		/*!
			Sets stepper direction to clockwise
		*/
		void dirSetCW();
		/*!
			Sets stepper direction to counterclockwise
		*/
		void dirSetCCW();
		/*!
			Returns if requested stepper motion is complete
		*/
		bool isDone();
		/*!
			Sets the target position to calculate the movement profile based on
		*/
		void setPos(long posDegree, int speed);
		/*!
			Sets the target position to calculate the movement profile based on
		*/
		void changePos(long posDegree, int speed);
		/*!
			Gets current motor position in degrees
		*/
		long getCurrentPosition();
		/*!
			Resets the accumulated motor position
		*/
		void resetPosition();
		/*!
			Sets the motor to break mode (no stepping but enabled)
		*/
		void setBrake();
		/*!
			Makes a full step of the motor
		*/
		void fullStep();
		/*!
			Increase the position by one step
		*/
		void incrementPos();
		/*!
			Gets the current direction of the motor
		*/
		int getDir();
		/*!
			Gets the current state of the motor
		*/
		stepperStates getState();
		/*!
			Set the acceleration value of the motor deg/s^2
		*/
    	void setAcceleration(long accelVal);
		/*!
			Set the deceleration value of the motor deg/s^2
		*/
    	void setDeceleration(long decelVal);
		/*!
			Get the current target acceleration value of the motor
		*/
    	long getAcceleration();
		/*!
			Get the current target decelerartion value of the motor
		*/
    	long getDeceleration();
		/*!
			Perform initial calculations for the motor movement controller
		*/
    	void calculateMoveProfile();
		/*!
			Returns the number of steps of planned acceleration
		*/
    	int getAccelSteps();
		/*!
			Returns the number of steps of planned deceleration
		*/
    	int getDecelSteps();
		/*!
			Perform the next step calculation for the motor movement controller
		*/
    	long calculateNextStep();
		/*!
			Returns the number of steps left in the current movement profile
		*/
    	long getRemainingSteps();
		/*!
			Returns the time to next step in microseconds
		*/
    	long getTimeToNext();


};



#endif