import sys
import cv2
import numpy as np
import pyzed.sl as sl
import robotpy_apriltag as at

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

tag_detector = at.AprilTagDetector()
tag_detector.addFamily("tag16h5")

def get_april_tag():
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
        zed.retrieve_image(image_zed, sl.VIEW.LEFT) # Get image from left camera
        zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH) # Get depth map
        zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA) # Get point cloud array

        image = cv2.cvtColor(image_zed.get_data(), cv2.COLOR_BGR2GRAY) # Convert image to B&W for AprilTag detection
        tags = tag_detector.detect(image) # Detect tags

        depths = []

        point_cloud_x = []
        point_cloud_y = []
        point_cloud_z = []
        depth = []
        tag_id = []

        debug_image = draw_tags(image_zed.get_data(), tags)

        key = cv2.waitKey(1)
        if key == 27:
            cv2.destroyAllWindows()
            sys.exit()
            
        cv2.imshow('AprilTags', debug_image)

        return point_cloud_x

def draw_tags(image, tags):
    for tag in tags:
        tag_id = tag.getId()
        center = tag.getCenter()

        corner_01 = tag.getCorner(0)
        corner_02 = tag.getCorner(1)
        corner_03 = tag.getCorner(2)
        corner_04 = tag.getCorner(3)

        cv2.circle(image, (center.x, center.y), 5, (0, 0, 255), 2)

        cv2.line(image, (corner_01.x, corner_01.y),
                (corner_02.x, corner_02.y), (255, 0, 0), 2)
        cv2.line(image, (corner_02.x, corner_02.y),
                (corner_03.x, corner_03.y), (255, 0, 0), 2)
        cv2.line(image, (corner_03.x, corner_03.y),
                (corner_04.x, corner_04.y), (0, 255, 0), 2)
        cv2.line(image, (corner_04.x, corner_04.y),
                (corner_01.x, corner_01.y), (0, 255, 0), 2)

        cv2.putText(image, str(tag_id), (center.x - 10, center.y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2, cv2.LINE_AA)

    return image