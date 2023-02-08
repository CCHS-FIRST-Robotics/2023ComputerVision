import sys
import cv2
import time
import copy
import math
import apriltag
import numpy as np
import pyzed.sl as sl

init = sl.InitParameters()

init.camera_resolution = sl.RESOLUTION.HD720 # Resolution 1280x720
init.camera_fps = 20
init.depth_mode = sl.DEPTH_MODE.PERFORMANCE # Options: (ULTRA, QUALITY, PERFORMANCE)

# Use a right-handed Y-up coordinate system (The OpenGL one)
init.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
init.coordinate_units = sl.UNIT.METER # Sets units in meters
init.depth_minimum_distance = 0.3 # Set the minimum depth perception distance to 30 cm
init.depth_maximum_distance = 20 # Set the maximum depth perception distance to 20 m

zed = sl.Camera()
status = zed.open(init)
if (status != sl.ERROR_CODE.SUCCESS):
    sys.exit(-1)

runtime = sl.RuntimeParameters()

runtime.confidence_threshold = 100
runtime.textureness_confidence_threshold = 100

image_zed = sl.Mat()
depth_map = sl.Mat()
point_cloud = sl.Mat()

resolution = zed.get_camera_information().camera_resolution
x = int(resolution.width / 2) # Center coordinates
y = int(resolution.height / 2)

tag_detector = apriltag.Detector(apriltag.DetectorOptions(families="tag36h11", nthreads=4))

def get_april_tag():
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
        zed.retrieve_image(image_zed, sl.VIEW.LEFT) # Get image from left camera
        zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH) # Get depth map
        zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA) # Get point cloud array

        image = cv2.cvtColor(image_zed.get_data(), cv2.COLOR_BGR2GRAY) # Convert image to B&W for AprilTag detection
        tags = tag_detector.detect(image) # Detect tags

        depths = []

        # Finds the depth of each AprilTag in the image
        for tag in tags:
            depths.append(depth_map.get_value(*tag.center))

        nearest_tag = None

        # Finds the AprilTag closest to the camera
        if depths:
            lowest_val = min(depths)
            nearest_tag = tags[depths.index(lowest_val)]
        else:
            return None # Return None if there are no AprilTags detected
        
        return point_cloud.get_value(nearest_tag.center) # Return point cloud values of nearest AprilTag