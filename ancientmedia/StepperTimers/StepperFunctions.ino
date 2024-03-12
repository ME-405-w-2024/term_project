//Stepper partamaters
int microSteps = 4;
int pulsesPerRev = 200;
int stepperDirection = 1;
int stepperStepPin = 0;
int stepperDirPin = 0;
int stepperM1 = 0;
int stepperM2 = 0;
int stepperM3 = 0;
int stepperEnablePin = 0;

//Speed variables
int targetSpeed = 0;
int currentSpeed = 0;
int targetDegPerSec = 0;
int currentDegPerSec = 0;

//Position variables
long pulsesPos = 0;
long targetPos = 0;
long targetPulses = 0;
long rampPos = 0;
long rampPosPulses = 0;

//States
bool stopped = false;
bool pulseState = false;
bool decelState = false;

//Constants
const int MIN_SPEED = 50;
const int MAX_SPEED = 300;



void setupStepper(int microsteps, int stepPerRev, int stepPin, int dirPin, int M1, int M2, int M3, int enablePin) {
  microSteps = microsteps;
  pulsesPerRev = stepPerRev;
  stepperStepPin = stepPin;
  stepperDirPin = dirPin;
  stepperM1 = M1;
  stepperM2 = M2;
  stepperM3 = M3;
  stepperEnablePin = enablePin;

  disableStepper();

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



void setStepperSpeed(int RPM) {
  targetSpeed = RPM;
  targetDegPerSec = RPM * 6;
  timer1ChangeFrequency(pulsesPerSecond(RPM) * 2, 8); //multipled by 2 because toggle
  timer1Enable();
  stopped = false;
}

void setTargetSpeed(int RPM) {
  targetSpeed = RPM;
  targetDegPerSec = RPM * 6;
  timer1Enable();
  stopped = false;
}

void updateStepperSpeed(int RPM) {
  targetSpeed = RPM;
  targetDegPerSec = RPM * 6;
  stopped = false;
}

int pulsesPerSecond(int RPM) {
  return ((long)RPM * pulsesPerRev * microSteps) / 60;
}

int stepMicros(int RPM) {
  return 1000000 / ((RPM * pulsesPerRev * microSteps) / 60);
}

int enableStepper() {
  digitalWrite(stepperEnablePin, 0);
}

int disableStepper() {
  digitalWrite(stepperEnablePin, 1);
}

int dirSetCW() {
  stepperDirection = 1;
  digitalWrite(stepperDirPin, HIGH);
  Serial.println("CW Direction");
}

int dirSetCCW() {
  stepperDirection = -1;
  digitalWrite(stepperDirPin, LOW);
  Serial.println("CCW Direction");
}

bool isDone() {
  return stopped;
}

long setPos(int posDegree, int RPM) {
  targetSpeed = RPM;
  targetPos = posDegree;
  targetPulses = ((long)posDegree * pulsesPerRev) / 360 * microSteps;

//  Serial.print("Target position: ");
//  Serial.println(targetPulses);

  if (targetPulses > pulsesPos) {
    dirSetCW();
    setStepperSpeed(RPM);
    rampPosPulses = targetPulses - (targetSpeed - MIN_SPEED);

  } else if  (targetPulses < pulsesPos) {
    dirSetCCW();
    setStepperSpeed(RPM);
    rampPosPulses = targetPulses + targetSpeed - MIN_SPEED;

  }

//  Serial.print("rampPosPulses: ");
//  Serial.println(rampPosPulses);
//  Serial.println();

}

long getPulsesPos() {
  return pulsesPos;
}

long resetPulsesPos() {
  pulsesPos = 0;
}


void setBrake() {
  timer1Disable();
  if (stopped != true) {
    digitalWrite(stepperStepPin, HIGH);
    stopped = true;
  }
  currentSpeed = 0;
  currentDegPerSec = 0;
}



ISR(TIMER1_COMPA_vect) { //stepper pulse gen


  pulseState = !pulseState;
  digitalWrite(stepperStepPin, pulseState);

  if (pulseState) { //only evaluate on pulse step

    pulsesPos += stepperDirection;

    if (decelState) { //In deceleration?

      if (currentSpeed <= MIN_SPEED) {
        currentSpeed = 0;
        decelState = false;
      } else {
        currentSpeed -= 1;
      }

    } else { //acceleration

      if (currentSpeed < MIN_SPEED) {
        currentSpeed = MIN_SPEED;
      } else if (currentSpeed < targetSpeed) {
        currentSpeed += 1;
      }

    }



  }




  if (pulsesPos == targetPulses) {
    setBrake();
    //disableStepper();
  } else if (pulsesPos == rampPosPulses) {
    decelState = true;

  }

  timer1UpdateFrequency(pulsesPerSecond(currentSpeed) * 2, 8);
}
