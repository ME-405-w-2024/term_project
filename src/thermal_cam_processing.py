# what do we want:
# input: camera obj
# output: angle to turn to
import math

class ThCamCalc:

    def __init__(self, cam_obj):

        self.camera = cam_obj
        # set up a default angle
        self.angle = 0


    def get_centroid(self):
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


    def get_angle(self):
        angle = 0
        return angle