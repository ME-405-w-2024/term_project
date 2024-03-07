import pyb
import time


PWM_PIN = pyb.Pin.board.PA0
PWM_PIN_TIMER_NUM = 2
PWM_PIN_TIMER_CHANNEL = 1

PWM_FREQUENCY = 50

MAX_PWM = 10

MIN_PWM = 5


if __name__ == "__main__":

    pwm_pin = pyb.Pin(PWM_PIN, pyb.Pin.OUT_PP)
    pwm_timer = pyb.Timer(PWM_PIN_TIMER_NUM, freq=PWM_FREQUENCY)
    timer_channel = pwm_timer.channel(PWM_PIN_TIMER_CHANNEL, pyb.Timer.PWM, pin=pwm_pin)

    

    timer_channel.pulse_width_percent(MAX_PWM)
    print(MAX_PWM)

    input()

    timer_channel.pulse_width_percent(MIN_PWM)
    print(MIN_PWM)

    print("Calubtrated?")