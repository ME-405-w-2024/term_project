

import cotask
import task_share
import pyb
import globaldefs
import platform
import time
import servo_driver
import micropython

if "MicroPython" not in platform.platform():
    from me405_support import cotask, cqueue, task_share



micropython.alloc_emergency_exception_buf(100)



def rpm_to_rad_s(rpm):
    print()
    return int(rpm/9.5493)


def percent_to_pwm(input, max_pwm, min_pwm):

    pwm_range = max_pwm-min_pwm

    pwm_percent = min_pwm + (pwm_range*input)

    return pwm_percent


if __name__ == "__main__":

    step_pin = pyb.Pin(globaldefs.DRV8825_STEP_PIN, pyb.Pin.OUT_PP)

    button_pin = pyb.Pin(globaldefs.ONBOARD_BUTTON_PIN, pyb.Pin.IN, pull=pyb.Pin.PULL_UP)

    step_timer = pyb.Timer(4, freq=(100000))    # freq in Hz


    stepper_i2c = pyb.I2C (1, pyb.I2C.CONTROLLER, baudrate=400000)
    


    ball_servo = servo_driver.ServoDriver(pwm_pin=globaldefs.SERVO_PWM_PIN, 
                                          pwm_timer_num=globaldefs.SERVO_PWM_PIN_TIMER_NUM,
                                          pwm_channel_num=globaldefs.SERVO_PWM_PIN_TIMER_CHANNEL,
                                          pwm_max_pulse=globaldefs.SERVO_MAX_PWM_US,
                                          pwm_min_pulse=globaldefs.SERVO_MIN_PWM_US,
                                          full_angle_range=globaldefs.SERVO_ANGLE_RANGE,
                                          period_ARR=globaldefs.SERVO_TIMER_ARR,
                                          period_PS=globaldefs.SERVO_TIMER_PS)


    flywheel_motor_pwm_pin = pyb.Pin(globaldefs.FLYWHEEL_MOTOR_PWM_PIN, pyb.Pin.OUT_PP)
    flywheel_motor_pwm_timer = pyb.Timer(globaldefs.FLYWHEEL_MOTOR_PWM_PIN_TIMER_NUM, freq=globaldefs.FLYWHEEL_MOTOR_PWM_FREQUENCY)
    flywheel_motor_pwm_timer_channel= flywheel_motor_pwm_timer.channel(globaldefs.FLYWHEEL_MOTOR_PWM_PIN_TIMER_CHANNEL, pyb.Timer.PWM, pin=flywheel_motor_pwm_pin)

    flywheel_pwm_value = percent_to_pwm(0, globaldefs.FLYWHEEL_MOTOR_MAX_PWM, globaldefs.FLYWHEEL_MOTOR_MIN_PWM)
    flywheel_motor_pwm_timer_channel.pulse_width_percent(flywheel_pwm_value)

    ball_servo.set_angle(180)


    target_rotation_speed = 30000

    rotation_acceleration = 60000

    rotation_deceleration = 60000

    pivot_target_deg = int(180*9.5)

    try:

        while 1:

            time.sleep(0.1)

            if(button_pin.value()==0):

                #Spin flywheel
                flywheel_pwm_value = percent_to_pwm(0.5, globaldefs.FLYWHEEL_MOTOR_MAX_PWM, globaldefs.FLYWHEEL_MOTOR_MIN_PWM)
                flywheel_motor_pwm_timer_channel.pulse_width_percent(flywheel_pwm_value)

                ball_servo.set_angle(180)

                #Delay to ensure flywheel spinup
                time.sleep(1)

                #Rotation start
                buffer = bytearray([pivot_target_deg>>8, pivot_target_deg, 
                                    target_rotation_speed>>8, target_rotation_speed,
                                    rotation_acceleration>>8, rotation_acceleration,
                                    rotation_deceleration>>8, rotation_deceleration])

                stepper_i2c.send(send=buffer,
                                 addr=globaldefs.STEPPER_I2C_ADDR)
                
                #Delay to complete rotation
                time.sleep(0.25)

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

                buffer = bytearray([(-1*pivot_target_deg)>>8, (-1*pivot_target_deg), 
                                    target_rotation_speed>>8, target_rotation_speed,
                                    rotation_acceleration>>8, rotation_acceleration,
                                    rotation_deceleration>>8, rotation_deceleration])
                
                stepper_i2c.send(send=buffer,
                                 addr=globaldefs.STEPPER_I2C_ADDR)

                


    except KeyboardInterrupt:

        flywheel_pwm_value = percent_to_pwm(0, globaldefs.FLYWHEEL_MOTOR_MAX_PWM, globaldefs.FLYWHEEL_MOTOR_MIN_PWM)
        flywheel_motor_pwm_timer_channel.pulse_width_percent(flywheel_pwm_value)
        flywheel_motor_pwm_timer.deinit() 

        ball_servo.set_angle(180)
        ball_servo.disable_stepper()

        print("PANIC")

        time.sleep(0.1)
        
        
            

        



