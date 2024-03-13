import globaldefs
import math

class driverTest:

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

            self.init_step_delay = math.sqrt((2*(globaldefs.STEP_MOTOR_ALPHA))/(accel)) * 1000000 * 0.95 #initial step delay based on input parameters
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

            return self.current_step_delay #in microseconds
    
    def isqrt(self, n):
        x = n
        y = (x + 1) // 2
        while y < x:
            x = y
            y = (x + n // x) // 2
        return x


    def get_next_delay_time(self):

        global new_step_delay
        global current_state

        if (current_state != globaldefs.AccelStates.stopped):

            #self.current_time_total += current_step_delay
            self.current_step += 1

            #print(self.current_step_delay)

        else:
            return (-1)
        

        if(self.current_step <= 2): #First value is weird and needs to be handled differently

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



        elif(current_state == globaldefs.AccelStates.running):

            if(self.current_step >= self.decel_begin_step):
                #print("Switching to decel")
                current_state = globaldefs.AccelStates.decelerating




        elif(current_state == globaldefs.AccelStates.decelerating):

            self.decel_steps += 1

            new_step_delay = (self.current_step_delay * ( (((4*self.decel_steps)-1)*1000) // (((4*self.decel_steps)+1)) ) ) // 1000

            #new_step_delay = ( self.init_step_delay * ( self.isqrt((-1*self.decel_steps*100)) - self.isqrt((-1*self.decel_steps-1)*100) ) ) // 10

            self.current_step_delay = new_step_delay
            

            if(self.current_step > self.step_pos - 2):
                #print("Stopping")
                current_state = globaldefs.AccelStates.stopped



        return (self.current_step_delay)

        
    def get_movement_state(self) -> int:
        global current_state
        return current_state


def rpm_to_rad_s(rpm):
    converted_value = rpm/9.5493
    print(converted_value)
    return int(converted_value)


if __name__ == "__main__":

    stepper_driver = driverTest()

    target_value = 1000

    target_speed = rpm_to_rad_s(300)

    acceleration = 1000

    deceleration = 1000

    initial_delay = stepper_driver.step_planner_setup(step_target=target_value, 
                                                        accel=acceleration, 
                                                        decel=deceleration, 
                                                        max_speed=target_speed)

    next_value = initial_delay
    # print(next_value)
    while (next_value > 0):
        print(next_value)
        next_value = stepper_driver.get_next_delay_time() #get the next time between steps