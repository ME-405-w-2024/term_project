import pyb
import utime

CHAN_NUM = 1
TIMER_NUM = 2
FREQ = 50


if __name__ == "__main__":

    pwm_pin = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP)
    pwm_timer = pyb.Timer (TIMER_NUM , freq=FREQ)
    timer_channel = pwm_timer.channel(CHAN_NUM, pyb.Timer.PWM, pin=pwm_pin)

    try:
        while 1:
            print("5% pulse")
            timer_channel.pulse_width_percent(5)
            utime.sleep(2)
            print("10% Pulse")
            timer_channel.pulse_width_percent(10)
            utime.sleep(2)
            print("15% Pulse")
            timer_channel.pulse_width_percent(15)
            utime.sleep(2)    
    except:
        timer_channel.pulse_width_percent(0)