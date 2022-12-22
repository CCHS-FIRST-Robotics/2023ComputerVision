import pyzed.sl as sl
def main() :
    # Create a ZED camera object
    zed = sl.Camera()
    # Set initial parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720 # Use HD720 video mode (default fps: 60)
    init_params.coordinate_units = sl.UNIT.METER # Set units in meters
    # Open the camera
    err = zed.open(init_params)
    if (err != sl.ERROR_CODE.SUCCESS) :
        print(repr(err))
        exit(-1)
 
    # Enable video recording
    record_params = RecordingParameters("myVideoFile.svo, sl.SVO_COMPRESSION_MODE.HD264)
    err = zed.enable_recording(record_params)
    if (err != sl.ERROR_CODE.SUCCESS) :
        print(repr(err))
        exit(-1)
 
    # Grab data during 500 frames
    i = 0
    while i < 500 :
        # Grab a new frame
        if zed.grab() == sl.ERROR_CODE.SUCCESS :
            # Record the grabbed frame in the video file
            i = i + 1
 
    zed.disable_recording()
    print("Video has been saved ...")
    zed.close()
    return 0
 
if __name__ == "__main__" :
    main()
