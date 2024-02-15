import pyb, time


PWM_PIN = pyb.Pin.board.PA0
PWM_PIN_TIMER_NUM = 2
PWM_PIN_TIMER_CHANNEL = 1
PWM_FREQUENCY = 30000





if __name__ == "__main__":

    pwm_pin = pyb.Pin(PWM_PIN, pyb.Pin.OUT_PP)
    pwm_timer = pyb.Timer (PWM_PIN_TIMER_NUM , freq=PWM_FREQUENCY)
    timer_channel = pwm_timer.channel(1, pyb.Timer.PWM, pin=pwm_pin)


    while 1:

        timer_channel.pulse_width_percent(90)
        time.sleep(2)
        timer_channel.pulse_width_percent(10)
        time.sleep(2)
