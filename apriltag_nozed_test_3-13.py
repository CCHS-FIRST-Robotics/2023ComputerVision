import robotpy_apriltag

import cv2
import time
import copy
import sys
import numpy as np
import math


def main():

    # Create a ZED camera
    vid = cv2.VideoCapture(0)

    # tag_detector = apriltag.Detector(apriltag.DetectorOptions(families="tag36h11"))
    detector = robotpy_apriltag.AprilTagDetector()
    detector.addFamily('tag16h5')

    elapsed_time = 0
    while True:
        start_time = time.time()

        
        ret, img = vid.read() 

        image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        tags = detector.detect(image)
        for tag in tags:
            distance = get_dist(tag.getCenter())

        debug_image = copy.deepcopy(image)

        debug_image = draw_tags(debug_image, tags, elapsed_time)
        elapsed_time = time.time() - start_time

        key = cv2.waitKey(1)
        if key == 27:
            break

        cv2.imshow('AprilTags', debug_image)

    cv2.destroyAllWindows()


def get_dist(point):
    return 1
    

def draw_tags(
    image,
    tags,
    elapsed_time,
):
    for tag in tags:
        tag_family = tag.getFamily()
        tag_id = tag.getId()
        center = tag.getCenter()
        corners = [(int(tag.getCorner(i).x), int(tag.getCorner(i).y)) for i in range(4)]

        center = (int(center.x), int(center.y))
        corner_01 = corners[0]
        corner_02 = corners[1]
        corner_03 = corners[2]
        corner_04 = corners[3]

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
