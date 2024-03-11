# what do we want:
# input: camera obj
# output: angle to turn to
import math

class ThCamCalc:

    def __init__(self, DIST_CAM, DIST_SHOOTER, FOV_ANG, NUM_PIXELS):

        self.DIST_CAM = DIST_CAM
        self.DIST_SHOOTER = DIST_SHOOTER

        # convert an input FOV in deg to rad
        self.FOV_ANG = math.radians(FOV_ANG)
        self.NUM_PIXELS = NUM_PIXELS
        # angular resolution in radians / pix
        self.ANG_RES = self.FOV_ANG / self.NUM_PIXELS

        # set up a default angle
        self.angle = 0


    def get_centroid(self, cam_obj):

        self.camera = cam_obj

        image = self.camera.get_image()

        #self.camera.ascii_art(image.v_ir)

        total_sum = 0
        weighted_sum_x = 0

        # iterate through lines in the csv
        for line in self.camera.get_csv(image.v_ir, limits=(0, 99)):
            # convert csv style data to an array
            line_arr = [ max(0, int(value)-50) for value in line.split(',')]
            print(line_arr)

            for i,x in enumerate(line_arr):
                total_sum += x
                weighted_sum_x += i*x

        if total_sum != 0:
            centroid_x = weighted_sum_x / total_sum
        else:
            centroid_x = 0

        centroid_x = centroid_x*10

        return centroid_x


    def get_angle(self, centroid_pix):
        
        # determine how far from the center of the thermal cam we are
        pix_from_center = centroid_pix - (self.NUM_PIXELS / 2)

        # convert to an angle for the thermal camera
        th_cam_angle = pix_from_center * self.ANG_RES

        # calculate a distance from the centerline
        y_dist = self.DIST_CAM * math.tan(th_cam_angle)

        # determine the angle relative to the shooter
        shooter_angle = math.degrees(math.atan(y_dist / self.DIST_SHOOTER))

        # offset by 180 deg
        shooter_angle += 180
        
        return shooter_angle
    

if __name__ == "__main__":
    
    calc = ThCamCalc(100, 200, 110, 32)
    centroid_test = 32

    print(calc.get_angle(centroid_test))