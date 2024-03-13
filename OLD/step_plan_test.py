import math 
import time
from enum import Enum


STEPS_PER_REV = 200
MICROSTEPS = 1

MICROSTEPS_PER_REV = STEPS_PER_REV*MICROSTEPS


ALPHA = (2*math.pi)/ MICROSTEPS_PER_REV #motor step angle α


class AccelStates(Enum):
    error = -1
    accelerating = 1
    running = 2
    decelerating = 3
    stopped = 4

# functional syntax
AccelStates = Enum('AccelStates', ['error', 'accelerating', 'running', 'decelerating', 'stopped'])



def move_to_pos_gen(step_pos, accel, decel, max_speed):
    """
        a [data] - Set acceleration (range: 71 - 32000)
        d [data] - Set deceleration (range: 71 - 32000)
        s [data] - Set speed (range: 12 - motor limit)
        m [data] - Move [data] steps (range: -64000 - 64000)
        move [steps] [accel] [decel] [speed]
        - Move with all parameters given
        <enter> - Repeat last move
        acc/dec data given in 0.01*rad/sec^2 (100 = 1 rad/sec^2)
        speed data given in 0.01*rad/sec (100 = 1 rad/sec)
        """
    
    current_step = 0 #The current overall position

    accel_step_count = 0 #the position relative to the accel state start

    

    max_step_accel_lim = (max_speed**2) / ((2*ALPHA) * accel * 100) #number of steps needed to accelerate to the desired speed

    accel_lim = (step_pos * decel) / (accel + decel) # number of steps before deceleration starts (disregarding desired speed)

    min_delay = 1/max_speed #minimum step delay

    init_step_delay = min_delay * math.sqrt((2*ALPHA)/(accel/100)) #initial step delay based on input parameters

    if (max_step_accel_lim <= accel_lim): #the acceleration is limited by reaching desired speed
        decel_val = - max_step_accel_lim * (accel / decel)
    else: #the acceleration is limited by deceleration start
        decel_val = -(step_pos - accel_lim)
        max_step_accel_lim = step_pos+decel_val

    current_state = AccelStates.accelerating

    current_step_delay = init_step_delay

    decel_step_count = decel_val

    current_time_total = 0

    while 1:

        if(current_state == AccelStates.accelerating):

            accel_step_count += 1

            new_step_delay = current_step_delay - (2*current_step_delay) / (4*accel_step_count)

            current_step_delay = new_step_delay

            if(current_step >= max_step_accel_lim):
                current_state = AccelStates.running



        elif(current_state == AccelStates.running):

            if(current_step >= step_pos+decel_val):
                current_state = AccelStates.decelerating




        elif(current_state == AccelStates.decelerating):

            decel_step_count += 1

            new_step_delay = current_step_delay - (2*current_step_delay) / (4*decel_step_count)

            current_step_delay = new_step_delay

            if(current_step >= step_pos):
                current_state = AccelStates.stopped




        if (current_state != AccelStates.stopped):

            current_time_total += current_step_delay
            current_step += 1

            #f.write(f"{current_time_total},{current_step}\n")

            yield (current_step_delay)

        else:
            yield (-1)


if __name__ == "__main__":
    gen = move_to_pos_gen(5000, 10, 10, 500)
