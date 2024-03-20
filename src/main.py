"""! @file main.py

This file lays out the main functionality of the shooting mechanism. 

"""  

import cotask
import task_share
import pyb
import globaldefs
import platform
import utime as time
import servo_driver
import micropython
from machine import I2C
from mlx_cam import MLX_Cam
from thermal_cam_processing import ThCamCalc

if "MicroPython" not in platform.platform():
    from me405_support import cotask, cqueue, task_share



micropython.alloc_emergency_exception_buf(100)


def rpm_to_rad_s(rpm):
    """! 
        Converts a RPM value to a Rad/Sec value
        @param rpm The input rpm to convert
        @returns The rotational speed in Rad/Sec
    """  
    return int(rpm/9.5493)


def percent_to_pwm(input, max_pwm, min_pwm):

    """! 
        Converts a standard 0-100 input to a PWM percent value based on given limits
        @param input The input percentage as a 0-100 value
        @param max_pwm The maximum PWM output corresponding to 100%
        @param min_pwm The minimum PWM output corresponding to 0%
        @returns The PWM percent pertaining to the input
    """  

    pwm_range = max_pwm-min_pwm

    pwm_percent = min_pwm + (pwm_range*input)

    return pwm_percent



if __name__ == "__main__":

    ##Pin object for the input button which starts the duel sequence
    button_pin = pyb.Pin(globaldefs.ONBOARD_BUTTON_PIN, pyb.Pin.IN, pull=pyb.Pin.PULL_UP)

    ##I2C object to communicate with the stepper driver controller
    stepper_i2c = pyb.I2C(1, pyb.I2C.CONTROLLER, baudrate=400000)


    
    # initialize thermal camera
    ##I2C object to communicate with the MLX camera
    cam_i2c = I2C(3, freq=3000000)
    ##MLX Camera object 
    therm_cam = MLX_Cam(cam_i2c)
    ##Thermal camera calculator object for returning useful targeting information
    therm_cam_calc = ThCamCalc(DIST_CAM=globaldefs.CAMERA_TARGET_DIST_IN,
                               DIST_SHOOTER=globaldefs.SHOOTER_TARGET_DIST_IN,
                               FOV_ANG=globaldefs.CAM_FOV_DEG,
                               NUM_PIXELS=globaldefs.CAM_X_PIXELS)

    

    ##Object to control the servo used to initiate firing
    ball_servo = servo_driver.ServoDriver(pwm_pin=globaldefs.SERVO_PWM_PIN, 
                                          pwm_timer_num=globaldefs.SERVO_PWM_PIN_TIMER_NUM,
                                          pwm_channel_num=globaldefs.SERVO_PWM_PIN_TIMER_CHANNEL,
                                          pwm_max_pulse=globaldefs.SERVO_MAX_PWM_US,
                                          pwm_min_pulse=globaldefs.SERVO_MIN_PWM_US,
                                          full_angle_range=globaldefs.SERVO_ANGLE_RANGE,
                                          period_ARR=globaldefs.SERVO_TIMER_ARR,
                                          period_PS=globaldefs.SERVO_TIMER_PS)

    ##Pin object to define the pin to be used for PWM control of the flywheel motor
    flywheel_motor_pwm_pin = pyb.Pin(globaldefs.FLYWHEEL_MOTOR_PWM_PIN, pyb.Pin.OUT_PP)
    ##Timer object for PWM control of the flywheel motor
    flywheel_motor_pwm_timer = pyb.Timer(globaldefs.FLYWHEEL_MOTOR_PWM_PIN_TIMER_NUM, freq=globaldefs.FLYWHEEL_MOTOR_PWM_FREQUENCY)
    ##Timer channel object for PWM control of the flywheel motor
    flywheel_motor_pwm_timer_channel= flywheel_motor_pwm_timer.channel(globaldefs.FLYWHEEL_MOTOR_PWM_PIN_TIMER_CHANNEL, pyb.Timer.PWM, pin=flywheel_motor_pwm_pin)

    ##Value of the PWM to be sent to the ESC to control the flywheel motor
    flywheel_pwm_value = percent_to_pwm(0, globaldefs.FLYWHEEL_MOTOR_MAX_PWM, globaldefs.FLYWHEEL_MOTOR_MIN_PWM)
    flywheel_motor_pwm_timer_channel.pulse_width_percent(flywheel_pwm_value)

    ball_servo.set_angle(180)

    ##Target speed of the rotation of the stepper motor in RPM
    target_rotation_speed = 10000
    ##Target acceleration of the stepper motor in (RPM/s)/10
    rotation_acceleration = 9000
    ##Target deceleration of the stepper motor in (RPM/s)/10
    rotation_deceleration = 9000
    ##Target position for the stepper motor to rotate to in deg
    pivot_target_deg = int(180*globaldefs.PULLEY_RATIO)

    ##Delay in ms to do pure targeting before switching to firing
    fire_delay = 4000

    ##The current position of the stepper motor in deg
    current_pos = 0

    ##The last position of the stepper motor in deg
    last_angle = 0

    ##The next/current position of the stepper motor in deg
    next_angle = 0

    ##Initial time at which the duel activation button was pressed
    press_time = 0

    ##Flag to determine if the motor is in an active duel/targeting 
    active = 0



    try:

        while 1:

            if(button_pin.value()==0):

                print("Start")

                press_time = time.ticks_ms()

                last_angle = 0

                current_pos = 0

                next_angle = 0

                active = 1
                

            if (active == 1):

                last_angle = next_angle

                ##The current detected centroid location
                centroid = therm_cam_calc.get_centroid(therm_cam)/10

                next_angle = therm_cam_calc.get_angle(centroid)

                next_angle = next_angle + globaldefs.CAM_TARGET_ANGLE_OFFSET

                ##The angle change between the last stepper angle and the next target angle
                angle_delta = (next_angle-last_angle)

                current_pos += angle_delta

                pivot_target_deg = int(angle_delta * globaldefs.PULLEY_RATIO)


                #Rotation start
                ##Data to send to the stepper controller
                buffer = bytearray([pivot_target_deg>>8, pivot_target_deg, 
                                    target_rotation_speed>>8, target_rotation_speed,
                                    rotation_acceleration>>8, rotation_acceleration,
                                    rotation_deceleration>>8, rotation_deceleration])

                stepper_i2c.send(buffer, globaldefs.STEPPER_I2C_ADDR)
                

                print(f"Targeting at: {angle_delta}, from centroid {centroid}")

                if((time.ticks_ms() - press_time) > fire_delay):

                    #Spin flywheel
                    flywheel_pwm_value = percent_to_pwm(0.2, globaldefs.FLYWHEEL_MOTOR_MAX_PWM, globaldefs.FLYWHEEL_MOTOR_MIN_PWM)
                    flywheel_motor_pwm_timer_channel.pulse_width_percent(flywheel_pwm_value)


                    #Delay to ensure flywheel spinup
                    time.sleep(1)

                    #Rotation start
                    buffer = bytearray([pivot_target_deg>>8, pivot_target_deg, 
                                        target_rotation_speed>>8, target_rotation_speed,
                                        rotation_acceleration>>8, rotation_acceleration,
                                        rotation_deceleration>>8, rotation_deceleration])

                    stepper_i2c.send(buffer, globaldefs.STEPPER_I2C_ADDR)
                    
                    #Delay to complete rotation
                    time.sleep(1)

                    #Fire ball
                    ball_servo.set_angle(180-30)

                    #Delay to ensure full speed when ball fired
                    time.sleep(0.25)

                    #Flywheel spindown
                    ball_servo.set_angle(180)
                    
                    flywheel_pwm_value = percent_to_pwm(0, globaldefs.FLYWHEEL_MOTOR_MAX_PWM, globaldefs.FLYWHEEL_MOTOR_MIN_PWM)
                    flywheel_motor_pwm_timer_channel.pulse_width_percent(flywheel_pwm_value)


                    #Delay to return to home when safe
                    time.sleep(1)

                    pivot_target_deg = int(current_pos * globaldefs.PULLEY_RATIO)

                    buffer = bytearray([(-1*pivot_target_deg)>>8, (-1*pivot_target_deg), 
                                        target_rotation_speed>>8, target_rotation_speed,
                                        rotation_acceleration>>8, rotation_acceleration,
                                        rotation_deceleration>>8, rotation_deceleration])
                    
                    stepper_i2c.send(buffer, globaldefs.STEPPER_I2C_ADDR)
                    
                    active = 0

                


    except KeyboardInterrupt:

        flywheel_pwm_value = percent_to_pwm(0, globaldefs.FLYWHEEL_MOTOR_MAX_PWM, globaldefs.FLYWHEEL_MOTOR_MIN_PWM)
        flywheel_motor_pwm_timer_channel.pulse_width_percent(flywheel_pwm_value)
        flywheel_motor_pwm_timer.deinit() 

        ball_servo.set_angle(180)
        ball_servo.disable_stepper()

        print("Exit")

        time.sleep(0.1)
        
    