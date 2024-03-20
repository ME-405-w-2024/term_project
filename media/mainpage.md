# Overview

## Description of code

The code is broken up into three main portions, the main control loop, the camera processing functions, and the remote stepper driver.

### Main Control Loop

The main control loop is contained in main.py. It initalizes all neccesary objects and local variables in order to run all of the functions of the launcher.

This includes:

- Camera Driver
- Servo Driver
- Stepper Driver Communication
- Button Polling
- State Control

as the main functions.

As for the sequence of events controlled by the main loop, the operation is given below. This is also reflected in the state diagram.

1. Wait for button to be pressed.
2. Begin continuous targeting using the camera data, which is used to yield a target angle.
3. After 4 seconds of continuous targeting, the flywheels are spun up.
4. After 1 second of spinup, the targeted position is held for 1 more second.
5. After this time, the ball-indexing servo is moved to fire the ball.
6. Another 1 second delay is given to allow the flywheels time to slow down.
7. The turret returns to its home position and waits for another button press.

No tasks were used, as all time-sensitive functions were either handled by timer interrupts (in the cases where PWM was needed), or were handled on separate controllers (in the case of the stepper driver)

### Remote Stepper Driver

The aiming platform is a turret-based system that is rotated by a belt-driven stepper motor.

To achieve full control over the stepper motor's motion profile, a separate microcontroller is used as a dedicated step planner and generator. The controller used was an arduino nano with firmware written in both standard C++ as well as Arduino's version of C in order to leverage the ease of use from the arduino ecosystem.

This system relies heavily on accurate timing and low calculation overhead in order to achieve maximum step speed and accuracy. Additionally, motion planning was important in order to utilize the maximum speed of the stepper motor without losing steps. To accomplish these goals, a version of the [stepper control algorithm as laid out by D. Austin](https://cdck-file-uploads-europe1.s3.dualstack.eu-west-1.amazonaws.com/arduino/original/3X/f/7/f7861c732d17db124bdc320398a31bc2023ce996.pdf) was implemented. The only notable change made to the math was a conversion to units of RPM from rad/sec. More information on using individual functions can be found in StepperDriver.

The remote board (containing its own stepper driving hardware, the arduino, and power conversion) was communicated with via I2C, and given information of requested position, motor speed and motor accelerations. All other calculation was handled by the microcontroller on the arduino, freeing up significant time on the STM32.

## State Diagram

![State Diagram](https://github.com/ME-405-w-2024/term_project/blob/main/media/StateDiagram.png?raw=true)
