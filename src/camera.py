import mediapipe as mp
import numpy as np
import cv2

class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.camera_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) 
        self.camera_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)


    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None
        # cvt color to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame


    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def __del__(self):
        self.close()
