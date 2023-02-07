import zed
from networktables import NetworkTables as nw


# Script runs on start up and handles networktables between RoboRIO and Jetson

nw.initialize(server="10.32.5.2") # Fill in later
tags = nw.getTable("tags")

def main():
    april_tag = zed.get_april_tag()
    send_april_tag(*april_tag)

def send_april_tag(x, y, z):
    tags.putNumber("x", x)
    tags.putNumber("y", y)
    tags.putNumber("z", z)


if __name__ == '__main__':
    main()