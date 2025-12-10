import cv2
import time
import numpy as np
from picamera2 import PiCamera2 # i am coding this blind lol

from src.common import consts

class CameraFeed():
    """
    Wraps around an opencv camera feed
    """
    def __init__(self, cam_id: int = 0) -> None:
        self.cam_id = cam_id
        
        self.camera = cv2.VideoCapture(self.cam_id) # get the opencv camera feed
        
        self.picam = PiCamera2()
        self.picam.start()
        time.sleep(0.1) # camera warmup


    def capture(self, cam_quality: int = consts.CAMERA_JPEG_COMPRESSION_VALUE) -> bytes:
        """
        gets and encodes a frame from the camera. returns the bytes of the encoded JPEG
        """
        # fetch frame
        #success, frame = self.camera.read()
        #if not success:
        #    print("failed frame read")
        #    return b''

        success, frame = True, self.picam.capture_array()

        # encode
        success, frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), cam_quality])
        if not success:
            print("failed frame encode")
            return b''
        
        return frame.tobytes() # convert to bytes and return
    