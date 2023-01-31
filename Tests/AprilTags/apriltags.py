import cv2
import time
import copy
import apriltag
import sys
import numpy as np
import pyzed.sl as sl
import math

def main():

    # Create a ZED camera
    zed = sl.Camera()

    # Create configuration parameters
    init_params = sl.InitParameters()
    init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE # Set the depth mode to performance (fastest)
    init_params.coordinate_units = sl.UNIT.METER  # Use meter units (for depth measurements)
    init_params.camera_resolution = sl.RESOLUTION.HD720

    # Open the camera
    err = zed.open(init_params)
    if (err!=sl.ERROR_CODE.SUCCESS):
        exit(-1)


    # Create and set RuntimeParameters after opening the camera
    runtime_parameters = sl.RuntimeParameters()
    runtime_parameters.sensing_mode = sl.SENSING_MODE.STANDARD  # Use STANDARD sensing mode

    # Setting the depth confidence parameters
    runtime_parameters.confidence_threshold = 100
    runtime_parameters.textureness_confidence_threshold = 100


    image_zed = sl.Mat()
    depth = sl.Mat()
    point_cloud = sl.Mat()

    mirror_ref = sl.Transform()
    mirror_ref.set_translation(sl.Translation(2.75,4.0,0))
    tr_np = mirror_ref.m

    tag_detector = apriltag.Detector(apriltag.DetectorOptions(families="tag36h11"))

    elapsed_time = 0
    while True:
        err = zed.grab(runtime_parameters)
        if err != sl.ERROR_CODE.SUCCESS : # A new image is available if grab() returns SUCCESS
            continue

        start_time = time.time()

        
        zed.retrieve_image(image_zed, sl.VIEW.LEFT) # Get the left image
        zed.retrieve_measure(depth, sl.MEASURE.DEPTH) # Retrieve depth Mat. Depth is aligned on the left image
        zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA) # Retrieve colored point cloud. Point cloud is aligned on the left image.
        


        image = cv2.cvtColor(image_zed.get_data(), cv2.COLOR_BGR2GRAY)
        tags = tag_detector.detect(image)
        for tag in tags:
            distance = get_dist(*tag.center, point_cloud)

        debug_image = copy.deepcopy(image_zed.get_data())

        debug_image = draw_tags(debug_image, tags, elapsed_time)
        elapsed_time = time.time() - start_time

        key = cv2.waitKey(1)
        if key == 27:
            break

        cv2.imshow('AprilTags', debug_image)

    cv2.destroyAllWindows()
    zed.close()


def get_dist(x, y, point_cloud):
    # Get and print distance value in mm at the center of the image
    # We measure the distance camera - object using Euclidean distance
    err, point_cloud_value = point_cloud.get_value(x, y)

    distance = math.sqrt(point_cloud_value[0] * point_cloud_value[0] +
                        point_cloud_value[1] * point_cloud_value[1] +
                        point_cloud_value[2] * point_cloud_value[2])

    #point_cloud_np = point_cloud.get_data()
    #point_cloud_np.dot(tr_np)

    if not np.isnan(distance) and not np.isinf(distance):
        print("Can't estimate distance at this position.")
        print("Your camera is probably too close to the scene, please move it backwards.\n")

    print("Distance to Camera at ({}, {}) (image center): {:1.3} m".format(x, y, distance), end="\r")
    sys.stdout.flush()
    return distance
    

def draw_tags(
    image,
    tags,
    elapsed_time,
):
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

    cv2.putText(image,
               "Elapsed Time:" + '{:.1f}'.format(elapsed_time * 1000) + "ms",
               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2,
               cv2.LINE_AA)

    return image


if __name__ == '__main__':
    main()
