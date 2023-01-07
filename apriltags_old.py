import cv2
import time
import copy
import apriltag
import sys
import numpy as np
import pyzed.sl as sl
import math

def main():

    # Set configuration parameters
	init_params = sl.InitParameters()
	init_params.depth_mode = sl.DEPTH_MODE.ULTRA # Use ULTRA depth mode
	init_params.coordinate_units = sl.UNIT.MILLIMETER # Use millimeter units (for depth measurements)

    # Open the camera
    err = zed.open(init)
    if err != sl.ERROR_CODE.SUCCESS :
        print(repr(err))
        zed.close()
        exit(1)

    # Set runtime parameters after opening the camera
    runtime = sl.RuntimeParameters()
    runtime.sensing_mode = sl.SENSING_MODE.STANDARD

    # Prepare new image size to retrieve half-resolution images
    image_size = zed.get_camera_information().camera_resolution
    image_size.width = image_size.width /2
    image_size.height = image_size.height /2

    # Declare your sl.Mat matrices
    image_zed = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)
    depth_image_zed = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)
    point_cloud = sl.Mat()

    # Create an RGBA sl.Mat object
    image_zed = sl.Mat(zed.get_camera_information().camera_resolution.width, zed.get_camera_information().camera_resolution.height, sl.MAT_TYPE.U8_C4)
    # Retrieve data in a numpy array with get_data()
    image_ocv = image_zed.get_data()
    print(image_zed.get_infos())


    tag_detector = apriltag.Detector(apriltag.DetectorOptions(families="tag36h11"))

    elapsed_time = 0
    while True:
        err = zed.grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS :
            start_time = time.time()

            # Retrieve the left image, depth image in the half-resolution
            zed.retrieve_image(image_zed, sl.VIEW.LEFT, sl.MEM.CPU, image_size)
            zed.retrieve_image(depth_image_zed, sl.VIEW.DEPTH, sl.MEM.CPU, image_size)
            # Retrieve the RGBA point cloud in half resolution
            zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA, sl.MEM.CPU, image_size)

            # To recover data from sl.Mat to use it with opencv, use the get_data() method
            # It returns a numpy array that can be used as a matrix with opencv
            image_ocv = image_zed.get_data()
            depth_image_ocv = depth_image_zed.get_data()

            debug_image = copy.deepcopy(image_ocv)

            image = cv2.cvtColor(image_ocv, cv2.COLOR_BGR2GRAY)
            tags = tag_detector.detect(image)
            for tag in tags:
                #print(tag.center)
                point3D = image_zed.get_value(*tag.center)[1]
                #print(point3D)
                distance = math.sqrt(point3D[0] * point3D[0] + point3D[1] *point3D[1] + point3D[2]*point3D[2])
                print(distance)

            debug_image = draw_tags(debug_image, tags, elapsed_time)
            elapsed_time = time.time() - start_time

            key = cv2.waitKey(1)
            if key == 27:
                break

            cv2.imshow('AprilTags', debug_image)

    cv2.destroyAllWindows()
    zed.close()

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
