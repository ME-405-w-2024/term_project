import pyb
#import time
import globaldefs
import math
import platform
import utime as time

if "MicroPython" not in platform.platform():
    from me405_support import cotask, cqueue, task_share



class DRV8825:

    #Need predefined globals to make timer interrupt work

    global new_step_delay
    new_step_delay = 0

    global current_state
    current_state = globaldefs.AccelStates.stopped

    global temp_value
    temp_value = 0

    def __init__(self):

        self.drv_step_pin = pyb.Pin(globaldefs.DRV8825_STEP_PIN, pyb.Pin.OUT_PP)
        self.drv_dir_pin = pyb.Pin(globaldefs.DRV8825_DIR_PIN, pyb.Pin.OUT_PP)
        self.drv_sleep_pin = pyb.Pin(globaldefs.DRV8825_SLEEP_PIN, pyb.Pin.OUT_PP)
        self.drv_reset_pin = pyb.Pin(globaldefs.DRV8825_RESET_PIN, pyb.Pin.OUT_PP)
        self.drv_enable_pin = pyb.Pin(globaldefs.DRV8825_ENABLE_PIN, pyb.Pin.OUT_PP)
        self.drv_m0_pin = pyb.Pin(globaldefs.DRV8825_M0_PIN, pyb.Pin.OUT_PP)
        self.drv_m1_pin = pyb.Pin(globaldefs.DRV8825_M1_PIN, pyb.Pin.OUT_PP)
        self.drv_m2_pin = pyb.Pin(globaldefs.DRV8825_M2_PIN, pyb.Pin.OUT_PP)

        self.movement_finished = True


    def set_full_step(self):
        self.drv_m0_pin.value(0)
        self.drv_m1_pin.value(0)
        self.drv_m2_pin.value(0)


    def set_dir(self, value: bool):
        self.drv_dir_pin.value(value)

    def set_sleep(self, value: bool):
        self.drv_sleep_pin.value(not value)

    def set_reset(self, value: bool):
        self.drv_reset_pin.value(not value)

    def set_enable(self, value: bool):
        self.drv_enable_pin.value(not value)

    #from https://ww1.microchip.com/downloads/en/Appnotes/doc8017.pdf
        
    def step_planner_setup(self, step_target, accel, decel, max_speed):

        global current_state

        """
        a [data] - Set acceleration (range: 71 - 32000)
        d [data] - Set deceleration (range: 71 - 32000)
        s [data] - Set speed (range: 12 - motor limit)
        m [data] - Move [data] steps (range: -64000 - 64000)
        move [steps] [accel] [decel] [speed]
        - Move with all parameters given
        <enter> - Repeat last move
        acc/dec data given in rad/sec^2 
        speed data given in rad/sec
        """

        self.step_pos = step_target

        print(f"max_speed: {max_speed}")

        self.accel_steps = (max_speed**2) / (2 * (globaldefs.STEP_MOTOR_ALPHA) * accel) #number of steps needed to accelerate to the desired speed

        accel_lim = (self.step_pos * decel) / (accel + decel) # number of steps before deceleration starts (disregarding desired speed)
        print(f"accel_lim: {accel_lim}")

        min_delay = 1/max_speed #minimum step delay

        self.init_step_delay = math.sqrt((2*(globaldefs.STEP_MOTOR_ALPHA))/(accel)) * 1000000 * 0.95#initial step delay based on input parameters
        self.init_step_delay = int(self.init_step_delay)
        print(f"init_step_delay: {self.init_step_delay}")


        if (self.accel_steps <= accel_lim): #the acceleration is limited by reaching desired speed
            self.decel_steps = - self.accel_steps * (accel / decel)
            print("Motor Reaches Full Speed")
        else: #the acceleration is limited by deceleration start
            self.decel_steps = -(self.step_pos - accel_lim)
            self.accel_steps = self.step_pos+self.decel_steps
            print("Motor is Accel/Decel Limited")



        self.current_step = 1 #The current overall position

        current_state = globaldefs.AccelStates.accelerating

        self.current_step_delay = int(self.init_step_delay) #do calculations in uS

        self.decel_steps = int(self.decel_steps)
        self.accel_steps = int(self.accel_steps)

        print(f"decel_step_count: {self.decel_steps}")
        print(f"accel_steps: {self.accel_steps}")

        self.current_time_total = 0

        self.decel_begin_step = self.step_pos + self.decel_steps

        self.movement_finished = False

        return self.current_step_delay #in microseconds


    def get_next_delay_time(self):

        global new_step_delay
        global current_state

        if (current_state != globaldefs.AccelStates.stopped):

            #self.current_time_total += current_step_delay
            self.current_step += 1

            #print(self.current_step_delay)

        else:
            self.movement_finished = True
            return (-1)
        

        if(current_state == globaldefs.AccelStates.running):

            if(self.current_step >= self.decel_begin_step):
                #print("Switching to decel")
                current_state = globaldefs.AccelStates.decelerating
                

        elif(self.current_step <= 2): #First value is weird and needs to be handled differently

            new_step_delay = (self.current_step_delay * ( ((self.current_step-1)*1000) // ((self.current_step+1)) ) ) // 1000

            #new_step_delay = ( self.init_step_delay * ( self.isqrt((self.current_step*100)) - self.isqrt((self.current_step-1)*100) ) ) // 10

            self.current_step_delay = new_step_delay
        

        elif(current_state == globaldefs.AccelStates.accelerating):

            new_step_delay = (self.current_step_delay * ( (((4*self.current_step)-1)*1000) // (((4*self.current_step)+1)) ) ) // 1000

            #new_step_delay = ( self.init_step_delay * ( self.isqrt((self.current_step*100)) - self.isqrt((self.current_step-1)*100) ) ) // 10

            self.current_step_delay = new_step_delay

            if(self.current_step >= self.accel_steps):
                #print("Switching to running")
                current_state = globaldefs.AccelStates.running


        elif(current_state == globaldefs.AccelStates.decelerating):

            self.decel_steps += 1

            new_step_delay = (self.current_step_delay * ( (((4*self.decel_steps)-1)*1000) // (((4*self.decel_steps)+1)) ) ) // 1000
            self.current_step_delay = new_step_delay
            
            temp_value = self.step_pos - 2

            if(self.current_step > temp_value):
                #print("Stopping")
                current_state = globaldefs.AccelStates.stopped


        return (self.current_step_delay)
        
    def is_move_finished(self) -> bool:
        return self.movement_finished



