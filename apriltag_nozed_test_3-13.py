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
        detected_ids = [tag.getId() for tag in detected_tags]

        ### FILTER OUT BAD TAGS ###
        # for each tag detected, increment its counter
        for tag in detected_tags:
            if tag.getId() not in counters:
                counters[tag.getId()] = 0
            counters[tag.getId()] += 1

        # If a tag id is not in the detected tags, reset its counter
        for tagId in counters.keys():
            if tagId not in detected_ids:
                counters[tagId] = 0

        tags = []
        for tag in detected_tags:
            is_fake = False
            # check if tag has a duplicate - 
            # if so, determine which is the real one based on how far it was from previous frame
            for tag2 in detected_tags:
                if tag.getId() == tag2.getId():
                    # If both tags suddenly showed up - discriminate based on how square they are
                    if tag.getId() not in prevTags:
                        if squareness(tag) > squareness(tag2):
                            is_fake = True
                        continue
                    # Otherwise, discriminate based on distance from where the tag previously was
                    tagId = tag.getId()
                    if get_dist_from_center(prevTags[tagId], tag) > get_dist_from_center(prevTags[tagId], tag2):
                        is_fake = True
        
            if is_fake:
                continue
            
            # more than 5 frames of detection -> real tag
            if counters[tag.getId()] > 10:
                tags.append(tag)

        prevTags = {tag.getId(): tag for tag in tags}

        if (len(tags) > 1):
            print(tags[0].getId(), tags[1].getId())

        debug_image = copy.deepcopy(image)

        debug_image = draw_tags(debug_image, tags, elapsed_time)
        elapsed_time = time.time() - start_time

        

        key = cv2.waitKey(1)
        if key == 27:
            break

        cv2.imshow('AprilTags', debug_image)

    cv2.destroyAllWindows()

def squareness(tag):
    corners = [(int(tag.getCorner(i).x), int(tag.getCorner(i).y)) for i in range(4)]
    dist1 = math.sqrt((corners[0][0] - corners[1][0])**2 + (corners[0][1] - corners[1][1])**2)
    dist2 = math.sqrt((corners[1][0] - corners[2][0])**2 + (corners[1][1] - corners[2][1])**2)
    return abs(dist1 - dist2)

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
