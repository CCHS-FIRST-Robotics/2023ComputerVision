import pyzed.sl as sl

init = sl.InitParameters()

init.camera_resolution = sl.RESOLUTION.HD720 # Resolution 1280x720
init.camera_fps = 15
init.depth_mode = sl.DEPTH_MODE.PERFORMANCE # Options: (ULTRA, QUALITY, PERFORMANCE)

# Use a right-handed Y-up coordinate system (The OpenGL one)
init.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
init.coordinate_units = sl.UNIT.METER # Sets units in meters
init.depth_minimum_distance = 0.3 # Set the minimum depth perception distance to 30 cm
init.depth_maximum_distance = 20 # Set the maximum depth perception distance to 20 m

zed = sl.Camera()
status = zed.open(init)

tracking_init = sl.PositionalTrackingParameters()
zed.enable_positional_tracking(tracking_init)

runtime = sl.RuntimeParameters()
camera_pose = sl.Pose()

translation = sl.Translation()
transform = sl.Transform()

depth_map = sl.Mat()
point_cloud = sl.Mat()

resolution = zed.get_camera_informations().camera_resolution
x = int(resolution.width / 2) # Center coordinates
y = int(resolution.height / 2)

def getData():
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
        zed.retreve_measure(depth_map, sl.MEASURE.DEPTH, sl.MEM.CPU)

        depth = depth_map.get_value(x, y, sl.MEM.CPU)
        return depth