import sys
import cv2
import copy
import numpy as np
import pyzed.sl as sl
from pupil_apriltags import Detector

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

fx = zed.get_camera_information().calibration_parameters.left_cam.fx
fy = zed.get_camera_information().calibration_parameters.left_cam.fy
cx = zed.get_camera_information().calibration_parameters.left_cam.cx
cy = zed.get_camera_information().calibration_parameters.left_cam.cy
camera_params = [fx, fy, cx, cy]

tag_detector = Detector(families="tag16h5", 
                        nthreads=2,
                        quad_decimate=2.0,
                        quad_sigma=0.8,
                        refine_edges=1,
                        decode_sharpening=0.25,
                        debug=0)

def get_april_tag():
    print("NEW FRAME")

    if zed.grab() == sl.ERROR_CODE.SUCCESS:
        zed.retrieve_image(image_zed, sl.VIEW.LEFT) # Get image from left camera
        zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH) # Get depth map
        zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA) # Get point cloud array

        image = cv2.cvtColor(image_zed.get_data(), cv2.COLOR_BGR2GRAY) # Convert image to B&W for AprilTag detection
        tags = tag_detector.detect(image, True, camera_params, 0.1524) # Detect tags

        point_cloud_x = []
        point_cloud_y = []
        point_cloud_z = []
        depth = []
        tag_id = []

        debug_image = copy.deepcopy(image_zed.get_data())

        debug_image = draw_tags(debug_image, tags)

        key = cv2.waitKey(1)
        if key == 27:
            cv2.destroyAllWindows()
            sys.exit()
            

        cv2.imshow('AprilTags', debug_image)

        # Finds the depth of each AprilTag in the image
        if tags:
            for tag in tags:
                err, point_cloud_value = point_cloud.get_value(*tag.center)

                point_cloud_x.append(point_cloud_value[0])
                point_cloud_y.append(point_cloud_value[1])
                point_cloud_z.append(point_cloud_value[2])
                depth.append(depth_map.get_value(*tag.center)[1])
                tag_id.append(tag.tag_id)

                print("-------")
                print(tag.pose_R)
                print(tag.pose_t)
                print(tag.pose_err)
                print(tag.tag_id)

        return point_cloud_x, point_cloud_y, point_cloud_z, depth, tag_id


def draw_tags(image, tags):
    for tag in tags:
        tag_family = tag.tag_family
        tag_id = tag.tag_id
        center = tag.center
        corners = tag.corners

        center = (int(center[0]), int(center[1]))
        corner_01 = (int(corners[0][0]), int(corners[0][1]))
        corner_02 = (int(corners[1][0]), int(corners[1][1]))
        corner_03 = (int(corners[2][0]), int(corners[2][1]))
        corner_04 = (int(corners[3][0]), int(corners[3][1]))

        cv2.circle(image, (center[0], center[1]), 5, (0, 0, 255), 2)

        cv2.line(image, (corner_01[0], corner_01[1]),
                (corner_02[0], corner_02[1]), (255, 0, 0), 2)
        cv2.line(image, (corner_02[0], corner_02[1]),
                (corner_03[0], corner_03[1]), (255, 0, 0), 2)
        cv2.line(image, (corner_03[0], corner_03[1]),
                (corner_04[0], corner_04[1]), (0, 255, 0), 2)
        cv2.line(image, (corner_04[0], corner_04[1]),
                (corner_01[0], corner_01[1]), (0, 255, 0), 2)

        cv2.putText(image, str(tag_id), (center[0] - 10, center[1] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2, cv2.LINE_AA)

    return image