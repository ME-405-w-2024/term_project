import pyb
import time


PWM_PIN = pyb.Pin.board.PA0
PWM_PIN_TIMER_NUM = 2
PWM_PIN_TIMER_CHANNEL = 1

ADC_PIN = pyb.Pin.board.PC0

PWM_FREQUENCY = 50

MAX_PWM = 10

MIN_PWM = 5

TEST_PWM = 10

ADC_MAX_INTEGER = 4095


def adc_to_pwm(input):

    percent_of_max = input/ADC_MAX_INTEGER

    pwm_range = MAX_PWM-MIN_PWM

    pwm_percent = MIN_PWM + (pwm_range*percent_of_max)

    return pwm_percent


if __name__ == "__main__":

    pwm_pin = pyb.Pin(PWM_PIN, pyb.Pin.OUT_PP)
    pwm_timer = pyb.Timer(PWM_PIN_TIMER_NUM, freq=PWM_FREQUENCY)
    timer_channel = pwm_timer.channel(PWM_PIN_TIMER_CHANNEL, pyb.Timer.PWM, pin=pwm_pin)


    adc_pin = pyb.ADC(ADC_PIN)

    
    

    timer_channel.pulse_width_percent(MIN_PWM)
    print(MIN_PWM)

    input()

    while 1:
       pwm_value = adc_to_pwm(adc_pin.read())
       timer_channel.pulse_width_percent(pwm_value)
       time.sleep(0.01)
