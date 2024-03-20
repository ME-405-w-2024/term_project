"""! @file thermal_cam_processing.py

Contains a class to perform relevant math operations to determine the centroid of thermal data.
This code is reliant on mlx_cam.py, which was provided as a driver for the thermal camera.

"""  

import math

class ThCamCalc:

    def __init__(self, DIST_CAM, DIST_SHOOTER, FOV_ANG, NUM_PIXELS):

        """!
            Creates a "calculator" object, setting up relevant distances and camera specifications.
            Assumes that the camera and shooter are aligned in the "y" plane.
            @param DIST_CAM Distance to the plane of the target to the camera.
            @param DIST_SHOOTER Distance to the plane of the target to the shooter pivot point.
            @param FOV_ANG Angular field of view for the camera.
            @param NUM_PIXELS Grid size in pixels of the camera. 
        """
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

        """!
            Determines the centroid of heat for a given camera object.
            This code takes a camera object as defined by mlx_cam.py and uses a weighted average
            of pixels to determine the centroid of in a single axis. 
            mlx_cam.get_csv is used to return comma separated heat values ranging from 0-100,
            and those values are filtered to return only hotspots. Said hotspots are then used for
            the centroid calculation. This function returns a pixel location of the centroid ranging from
            0-(self.NUM_PIXELS)
            @param cam_obj A thermal camera object from mlx_cam.py
        """

        self.camera = cam_obj

        image = self.camera.get_image()

        #self.camera.ascii_art(image.v_ir)

        total_sum = 0
        weighted_sum_x = 0

        # iterate through lines in the csv
        for line in self.camera.get_csv(image, limits=(0, 99)):
            # convert csv style data to an array
            line_arr = []
            thresh = 85
            for idx,val in enumerate(line.split(',')):
                if (int(val) > thresh):
                    line_arr.append(99)
                else:
                    line_arr.append(0)
            
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
        
        """!
            Intakes a given centroid and returns an angle to turn for the shooter.
            This function takes previously established distances and angular resolution
            and calculates a desired angle to turn for the shooter.
            @param centroid_pix A heat centroid location given in pixels. Intended to be the output from self.get_centroid()
        """

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