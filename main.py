import zed
from networktables import NetworkTables as nw

# Script runs on start up and handles networktables between RoboRIO and Jetson

nw.initialize(server="10.32.5.2") # IP Address of RoboRIO
tags = nw.getTable("tags") # AprilTag table

def main():
    while True:
        april_tag = zed.get_april_tag() # Publish AprilTag xyz vals

        # Send vals over networktables if apriltag exists
        if april_tag is not None:
            send_april_tag(*april_tag)

def send_april_tag(x, y, z):
    tags.putNumber("x", x)
    tags.putNumber("y", y)
    tags.putNumber("z", z)


if __name__ == '__main__':
    main()