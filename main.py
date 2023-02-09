import zed
from networktables import NetworkTables as nw

# Script runs on start up and handles networktables between RoboRIO and Jetson

nw.initialize(server="10.32.5.2") # IP Address of RoboRIO
tags = nw.getTable("tags") # AprilTag table

def main():
    x, y, z, depth, tag_id = zed.get_april_tag() # Publish AprilTag xyz vals

    # Send vals over networktables if apriltag exists
    if tag_id is not None:
        send_april_tag(x, y, z, depth, tag_id)

def send_april_tag(x, y, z, depth, tag_id):
    tags.putNumberArray("x", x)
    tags.putNumberArray("y", y)
    tags.putNumberArray("z", z)
    tags.putNumberArray("depth", depth)
    tags.putNumberArray("tag_id", tag_id)


if __name__ == '__main__':
    main()