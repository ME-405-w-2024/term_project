"""! @file globaldefs.py

Serves as an outline of constants that are used multiple times throughout the code.
Pin definitions for GPIO are defined here to provide a central source of truth. 

"""  

import pyb

##I2C address of the stepper controller
STEPPER_I2C_ADDR = 105

##Pin of the PWM input for the flywheel motor ESC
FLYWHEEL_MOTOR_PWM_PIN = pyb.Pin.board.PB10
##Timer number corresponding to the ESC pwm pin
FLYWHEEL_MOTOR_PWM_PIN_TIMER_NUM = 2
##Timer channel number corresponding to the ESC pwm pin
FLYWHEEL_MOTOR_PWM_PIN_TIMER_CHANNEL = 3

##Frequency of the PWM signal for the ESC
FLYWHEEL_MOTOR_PWM_FREQUENCY = 50

##PWM percentage for max speed on the ESC
FLYWHEEL_MOTOR_MAX_PWM = 10
##PWM percentage for min speed on the ESC
FLYWHEEL_MOTOR_MIN_PWM = 5

##Max integer value of the internal adc
ADC_MAX_INTEGER = 4095

##Pin location of the onboard blue button
ONBOARD_BUTTON_PIN = pyb.Pin.board.PC13

##Distance in inches from the target to the camera
CAMERA_TARGET_DIST_IN = 200#192
##Distance in inches from the target to the turret/launcher
SHOOTER_TARGET_DIST_IN = 300#192-60-30
##FOV of the camera in degrees
CAM_FOV_DEG = 55
##Pixels in the horizontal direction for the camera
CAM_X_PIXELS = 32

##Calibration offset for camera aiming
CAM_TARGET_ANGLE_OFFSET = 0

##Ratio of the rotation motor to the actual turret
PULLEY_RATIO = 9.5

##Pin of the PWM input for servo position control
SERVO_PWM_PIN = pyb.Pin.board.PA9
##Timer number corresponding to the servo PWM pin
SERVO_PWM_PIN_TIMER_NUM = 1
##Timer channel number corresponding to the servo PWM pin
SERVO_PWM_PIN_TIMER_CHANNEL = 2

# constants to set servo freq to 50hz w/ tick int of 1us
##Auto-reset value for the servo PWM generator
SERVO_TIMER_ARR = 19999
##Timer prescaler for the servo PWM generator
SERVO_TIMER_PS = 79

##Pulse width corresponding to the maximum position of the servo
SERVO_MAX_PWM_US = 2600
##Pulse width corresponding to the minimum position of the servo
SERVO_MIN_PWM_US = 600
##Range of motion for the servo
SERVO_ANGLE_RANGE = 180

