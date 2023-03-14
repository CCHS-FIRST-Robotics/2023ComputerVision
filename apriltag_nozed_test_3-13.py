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
    prevTags = {}
    counters = {}
    while True:
        start_time = time.time()

        
        ret, img = vid.read() 

        image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        detected_tags = detector.detect(image)
        tags = []

        # OLD METHOD OF FILTERING
        # for tag in detected_tags:
        #     dist = 0
        #     matching = False
        #     for prevTag in prevTags.values():
        #         if tag.getId() == prevTag.getId():
        #             matching = True
        #             dist = get_dist_from_center(tag, prevTag)
        #     if tag.getId() < 10 and dist < 20 and is_square(tag) and (matching or len(prevTags) == 0):
        #         tags.append(tag)
        #     distance = get_dist(tag.getCenter())

        for tag in detected_tags:
            if tag.getId() not in counters:
                counters[tag.getId()] = 0
            counters[tag.getId()] += 1

        prevTags = {tag.getId(): tag for tag in detected_tags}
        for tagId in counters.keys():
            if tagId not in prevTags.keys():
                counters[tagId] = 0

        for tag in detected_tags:
            if counters[tag.getId()] > 10:
                tags.append(tag)

        debug_image = copy.deepcopy(image)

        debug_image = draw_tags(debug_image, tags, elapsed_time)
        elapsed_time = time.time() - start_time

        key = cv2.waitKey(1)
        if key == 27:
            break

        cv2.imshow('AprilTags', debug_image)

    cv2.destroyAllWindows()

def is_square(tag):
    corners = [(int(tag.getCorner(i).x), int(tag.getCorner(i).y)) for i in range(4)]
    dist1 = math.sqrt((corners[0][0] - corners[1][0])**2 + (corners[0][1] - corners[1][1])**2)
    dist2 = math.sqrt((corners[1][0] - corners[2][0])**2 + (corners[1][1] - corners[2][1])**2)
    if abs(dist1 - dist2) < 5:
        return True

def get_dist_from_center(tag1, tag2):
    center1 = tag1.getCenter()
    center2 = tag2.getCenter()
    dist = math.sqrt((center1.x - center2.x)**2 + (center1.y - center2.y)**2)
    return dist

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
