import tag
import zed
from networktables import NetworkTables as nw


# Script runs on start up and handles networktables between RoboRIO and Jetson

nw.initialize(server="X.X.X.X") # Fill in later
state = nw.getTable("state")

def main():
    print(zed.get_april_tag())

def send_state(x_pos, y_pos, heading):
    state.putNumber("x_pos", x_pos)
    state.putNumber("y_pos", y_pos)
    state.putNumber("heading", heading)

if __name__ == '__main__':
    main()