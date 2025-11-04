import cv2
import numpy as np

class CameraFeed():
    def __init__(self, cam_id: int = 0, cam_quality: int = 100) -> None:
        self.cam_id = cam_id
        self.cam_quality = cam_quality
        
        self.camera = cv2.VideoCapture(self.cam_id)

    def capture(self) -> bytes:
        # fetch frame
        success, frame = self.camera.read()
        if not success:
            print("failed frame read")
            return b''

        # encode
        frame = cv2.resize(frame, (500, 500))
        success, frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.cam_quality])
        if not success:
            print("failed frame encode")
            return b''
        
        return frame.tobytes()