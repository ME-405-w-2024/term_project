// @file TimerFunctions.h

#ifndef TIMER_FUNC_H
#define TIMER_FUNC_H

#include<Arduino.h>

	#define TIMER0_DISABLE() TIMSK0 = 0
	#define TIMER0_ENABLE() TIMSK0 |= (1 << OCIE0A)
	#define TIMER0_RESET() TCNT0  = 0


	void timer0Setup();
	void timer1Setup();
	void timer0ChangeFrequency(long frequencyHZ, int preScaler);
	void timer1ChangeFrequency(long frequencyHZ, int preScaler);
	void timer1UpdateFrequency(long frequencyHZ, int preScaler);
	void timer1Disable();
	void timer1Enable();


#endif