import pyb, time
import pindefs as pins


PWM_PIN = pins.DRV8825_STEP_PIN
PWM_PIN_TIMER_NUM = pins.DRV8825_STEP_PIN_TIMER_NUM
PWM_PIN_TIMER_CHANNEL = pins.DRV8825_STEP_PIN_TIMER_CHAN
PWM_FREQUENCY = 100
 

class DRV8825:


    def __init__(self):
        
        self.drv_dir_pin = pyb.Pin(pins.DRV8825_DIR_PIN, pyb.Pin.OUT_PP)
        self.drv_sleep_pin = pyb.Pin(pins.DRV8825_SLEEP_PIN, pyb.Pin.OUT_PP)
        self.drv_reset_pin = pyb.Pin(pins.DRV8825_RESET_PIN, pyb.Pin.OUT_PP)
        self.drv_enable_pin = pyb.Pin(pins.DRV8825_ENABLE_PIN, pyb.Pin.OUT_PP)
        self.drv_m0_pin = pyb.Pin(pins.DRV8825_M0_PIN, pyb.Pin.OUT_PP)
        self.drv_m1_pin = pyb.Pin(pins.DRV8825_M1_PIN, pyb.Pin.OUT_PP)
        self.drv_m2_pin = pyb.Pin(pins.DRV8825_M2_PIN, pyb.Pin.OUT_PP)


    def set_full_step(self):
        self.drv_m0_pin.low()
        self.drv_m1_pin.high()
        self.drv_m2_pin.low()


    def set_dir(self, value):
        self.drv_dir_pin.value(value)

    def set_sleep(self, value):
        self.drv_sleep_pin.value(value)

    def set_reset(self, value):
        self.drv_reset_pin.value(value)

    def set_enable(self, value):
        self.drv_enable_pin.value(value)








if __name__ == "__main__":

    pwm_pin = pyb.Pin(PWM_PIN, pyb.Pin.OUT_PP)
    pwm_timer = pyb.Timer(PWM_PIN_TIMER_NUM, freq=PWM_FREQUENCY)
    timer_channel = pwm_timer.channel(PWM_PIN_TIMER_CHANNEL, pyb.Timer.PWM, pin=pwm_pin)

    timer_channel.pulse_width_percent(50)


    stepper_driver = DRV8825()

    stepper_driver.set_full_step()
    stepper_driver.set_sleep(1)
    stepper_driver.set_reset(1)
    
    stepper_driver.set_dir(0)

    

    stepper_driver.set_enable(0)

    target_value = 20000

    step_value = 5

    ramp_time = 2


    while 1:

        stepper_driver.set_enable(1)
        pwm_timer.freq(1000)
        
        time.sleep(2)

        stepper_driver.set_enable(0)

        value = 0

        for value in range(int(target_value/step_value)):

            pwm_timer.freq((value*step_value)+1)
            timer_channel.pulse_width_percent(50)

            #time.sleep(ramp_time/target_value)


        pwm_timer.freq(target_value)
        timer_channel.pulse_width_percent(50)

        time.sleep(2)



