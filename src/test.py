from thermal_cam_processing import ThCamCalc
import globaldefs

therm_cam_calc = ThCamCalc(DIST_CAM=globaldefs.CAMERA_TARGET_DIST_IN,
                               DIST_SHOOTER=globaldefs.SHOOTER_TARGET_DIST_IN,
                               FOV_ANG=globaldefs.CAM_FOV_DEG,
                               NUM_PIXELS=globaldefs.CAM_X_PIXELS)

for centroid in range(256):

    next_angle = therm_cam_calc.get_angle(centroid)

    print(f"{centroid}, {next_angle}")
    