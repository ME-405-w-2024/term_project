# import pyb
# import time


# PWM_PIN = pyb.Pin.board.PA0
# PWM_PIN_TIMER_NUM = 2
# PWM_PIN_TIMER_CHANNEL = 1

# ADC_PIN = pyb.Pin.board.PC0

# PWM_FREQUENCY = 50

# MAX_PWM = 10

# MIN_PWM = 5

# TEST_PWM = 10

# ADC_MAX_INTEGER = 4095


# def adc_to_pwm(input):

#     percent_of_max = input/ADC_MAX_INTEGER

#     pwm_range = MAX_PWM-MIN_PWM

#     pwm_percent = MIN_PWM + (pwm_range*percent_of_max)

#     return pwm_percent


# if __name__ == "__main__":

#     pwm_pin = pyb.Pin(PWM_PIN, pyb.Pin.OUT_PP)
#     pwm_timer = pyb.Timer(PWM_PIN_TIMER_NUM, freq=PWM_FREQUENCY)
#     timer_channel = pwm_timer.channel(PWM_PIN_TIMER_CHANNEL, pyb.Timer.PWM, pin=pwm_pin)


#     adc_pin = pyb.ADC(ADC_PIN)

    
    

#     timer_channel.pulse_width_percent(MIN_PWM)
#     print(MIN_PWM)

#     input()

#     while 1:
#        pwm_value = adc_to_pwm(adc_pin.read())
#        timer_channel.pulse_width_percent(pwm_value)
#        time.sleep(0.01)

import cotask
import task_share
import gc
import DRV8825_driver
import pyb
import globaldefs
import platform
import time
import sys

if "MicroPython" not in platform.platform():
    from me405_support import cotask, cqueue, task_share


import micropython
micropython.alloc_emergency_exception_buf(100)

stepper_driver = DRV8825_driver.DRV8825()

global next_value
next_value = 0

global new_delay
new_delay = 0

global start_time
start_time = 0
global delta_time
delta_time = time.time_ns()


def step_next_irq(timer: pyb.Timer):
    global start_time
    global delta_time

    start_time = time.time_ns()

    global next_value
    global new_delay

    if (stepper_driver.drv_step_pin.value() == 1) : #if pulse is high, set it low and dont recalculate time
        stepper_driver.drv_step_pin.value(0) #end high pulse

    else: 
        next_value = stepper_driver.get_next_delay_time() #get the next time between steps

        stepper_driver.drv_step_pin.value(1) #begin high pulse

        #print(next_value)
        if (next_value > 0):    

            #scale delay to get a timer period and divide by 2 to get time for high and low edges of pulse
            new_delay = ((next_value-globaldefs.STEPPER_OVERHEAD_EST_US)*1000) // 2 // globaldefs.TIM4_SCALED_TICK_PERIOD_NS

            timer.period(new_delay)

    delta_time = time.time_ns() - start_time
    print(delta_time)

            

def rpm_to_rad_s(rpm):
    print()
    return int(rpm/9.5493)

def rotate_to(motor_driver: DRV8825_driver.DRV8825, stepper_timer: pyb.Timer, deg: float, target_speed, acceleration, deceleration):

    motor_driver.set_full_step()
    motor_driver.set_sleep(False)
    motor_driver.set_reset(False)
    
    motor_driver.set_dir(True)

    motor_driver.set_enable(True)
    time.sleep(0.01)
    

    target_value = int( (deg/360) * globaldefs.PULLEY_RATIO * globaldefs.STEP_MOTOR_STEP_PER_REV )

    initial_delay = motor_driver.step_planner_setup(step_target=target_value, 
                                                        accel=acceleration, 
                                                        decel=deceleration, 
                                                        max_speed=target_speed)
                   
    stepper_timer.prescaler(globaldefs.TIM4_PRESCALER)

    new_delay = ((initial_delay-globaldefs.STEPPER_OVERHEAD_EST_US)*1000)//globaldefs.TIM4_SCALED_TICK_PERIOD_NS
    stepper_timer.period(new_delay)

    print(f"First stepper time period: {stepper_timer.period()}")

    stepper_timer.callback(step_next_irq)


def end_rotate(motor_driver: DRV8825_driver.DRV8825, stepper_timer: pyb.Timer):
    motor_driver.set_enable(False)
    stepper_timer.deinit()


def percent_to_pwm(input, max_pwm, min_pwm):

    pwm_range = max_pwm-min_pwm

    pwm_percent = min_pwm + (pwm_range*input)

    return pwm_percent


if __name__ == "__main__":

    step_pin = pyb.Pin(globaldefs.DRV8825_STEP_PIN, pyb.Pin.OUT_PP)

    button_pin = pyb.Pin(globaldefs.ONBOARD_BUTTON_PIN, pyb.Pin.IN, pull=pyb.Pin.PULL_UP)

    step_timer = pyb.Timer(4, freq=(100000))    # freq in Hz


    flywheel_motor_pwm_pin = pyb.Pin(globaldefs.FLYWHEEL_MOTOR_PWM_PIN, pyb.Pin.OUT_PP)
    flywheel_motor_pwm_timer = pyb.Timer(globaldefs.FLYWHEEL_MOTOR_PWM_PIN_TIMER_NUM, freq=globaldefs.FLYWHEEL_MOTOR_PWM_FREQUENCY)
    flywheel_motor_pwm_timer_channel= flywheel_motor_pwm_timer.channel(globaldefs.FLYWHEEL_MOTOR_PWM_PIN_TIMER_CHANNEL, pyb.Timer.PWM, pin=flywheel_motor_pwm_pin)

    flywheel_pwm_value = percent_to_pwm(0, globaldefs.FLYWHEEL_MOTOR_MAX_PWM, globaldefs.FLYWHEEL_MOTOR_MIN_PWM)
    flywheel_motor_pwm_timer_channel.pulse_width_percent(flywheel_pwm_value)


    servo_pwm_pin = pyb.Pin(globaldefs.SERVO_PWM_PIN, pyb.Pin.OUT_PP)
    servo_pwm_timer = pyb.Timer(globaldefs.SERVO_PWM_PIN_TIMER_NUM, freq=globaldefs.SERVO_PWM_FREQUENCY)
    servo_pwm_timer_channel= servo_pwm_timer.channel(globaldefs.SERVO_PWM_PIN_TIMER_CHANNEL, pyb.Timer.PWM, pin=servo_pwm_pin)

    servo_pwm_value = percent_to_pwm(0, globaldefs.SERVO_MAX_PWM, globaldefs.SERVO_MIN_PWM)
    servo_pwm_timer_channel.pulse_width_percent(servo_pwm_value)


    target_rotation_speed = rpm_to_rad_s(600)

    rotation_acceleration = 500

    rotation_deceleration = 1000

    pivot_target_deg = 180

    try:

        while 1:


            if(stepper_driver.is_move_finished()):
                #end_rotate(stepper_driver, step_timer)

                flywheel_pwm_value = percent_to_pwm(0, globaldefs.FLYWHEEL_MOTOR_MAX_PWM, globaldefs.FLYWHEEL_MOTOR_MIN_PWM)
                flywheel_motor_pwm_timer_channel.pulse_width_percent(flywheel_pwm_value)


                if(button_pin.value()==0):

                    
                    flywheel_pwm_value = percent_to_pwm(0.3, globaldefs.FLYWHEEL_MOTOR_MAX_PWM, globaldefs.FLYWHEEL_MOTOR_MIN_PWM)
                    flywheel_motor_pwm_timer_channel.pulse_width_percent(flywheel_pwm_value)

                    time.sleep(2)

                    servo_pwm_value = percent_to_pwm(0, globaldefs.SERVO_MAX_PWM, globaldefs.SERVO_MIN_PWM)
                    servo_pwm_timer_channel.pulse_width_percent(servo_pwm_value)

                    time.sleep(1)

                    flywheel_pwm_value = percent_to_pwm(0, globaldefs.FLYWHEEL_MOTOR_MAX_PWM, globaldefs.FLYWHEEL_MOTOR_MIN_PWM)
                    flywheel_motor_pwm_timer_channel.pulse_width_percent(flywheel_pwm_value)

                    #rotate_to(stepper_driver, step_timer, pivot_target_deg, target_rotation_speed, rotation_acceleration, rotation_deceleration)

    except KeyboardInterrupt:

        flywheel_pwm_value = percent_to_pwm(0, globaldefs.FLYWHEEL_MOTOR_MAX_PWM, globaldefs.FLYWHEEL_MOTOR_MIN_PWM)
        flywheel_motor_pwm_timer_channel.pulse_width_percent(flywheel_pwm_value)
        flywheel_motor_pwm_timer.deinit() 
        print("PANIC")
                
            
            
        time.sleep(0.1)
        
        
            

        



