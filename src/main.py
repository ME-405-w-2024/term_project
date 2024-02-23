import pyb


PWM_PIN = pyb.Pin.board.PA0
PWM_PIN_TIMER_NUM = 2
PWM_PIN_TIMER_CHANNEL = 1

PWM_FREQUENCY = 30000


if __name__ == "__main__":

    pwm_pin = pyb.Pin(PWM_PIN, pyb.Pin.OUT_PP)
    pwm_timer = pyb.Timer(PWM_PIN_TIMER_NUM, freq=PWM_FREQUENCY)
    timer_channel = pwm_timer.channel(PWM_PIN_TIMER_CHANNEL, pyb.Timer.PWM, pin=pwm_pin)

    timer_channel.pulse_width_percent(95)

    while 1:
        pass