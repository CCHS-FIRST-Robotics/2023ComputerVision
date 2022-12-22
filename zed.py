import sys
import pyzed.sl as sl
import networktables as fw
import ogl_viewer.viewer as gl

def main():
    init = sl.InitParameters()

    init.camera_resolution = sl.RESOLUTION.HD720 # Resolution 1280x720
    init.camera_fps = 30
    init.depth_mode = sl.DEPTH_MODE.QUALITY # Options: (ULTRA, QUALITY, PERFORMANCE)

    # Use a right-handed Y-up coordinate system (The OpenGL one)
    init.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
    init.coordinate_units = sl.UNIT.METER # Sets units in meters
    init.depth_minimum_distance = 0.3 # Set the minimum depth perception distance to 30 cm
    init.depth_maximum_distance = 20 # Set the maximum depth perception distance to 20 m

    zed = sl.Camera()
    status = zed.open(init)

    # tracking_parameters = sl.PositionalTrackingParameters()
    # err = zed.enable_tracking(tracking_parameters)

    if (status != sl.ERROR_CODE.SUCCESS):
        print(repr(status))
        sys.exit(-1)

    res = sl.Resolution()
    res.width = 720
    res.height = 404

    camera_model = zed.get_camera_information().camera_model
    # Create OpenGL viewer
    viewer = gl.GLViewer()
    viewer.init(len(sys.argv), sys.argv, camera_model, res)

    point_cloud = sl.Mat(res.width, res.height, sl.MAT_TYPE.F32_C4, sl.MEM.CPU)

    while viewer.is_available():
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA,sl.MEM.CPU, res)
            viewer.updateData(point_cloud)

    viewer.exit()
    zed.close()

if __name__ == '__main__':
    main()