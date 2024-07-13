from pyray import *
import sys
import os

from src.hand import HandDetector
from src.face import FaceDetector
from src.camera import Camera

WIDTH = HEIGHT = 800

def main():
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    set_trace_log_level(LOG_NONE)
    init_window(WIDTH, HEIGHT, "Avatar")
    set_target_fps(60)
    camera = Camera()
    hand_detector = HandDetector()
    face_detector = FaceDetector()
    while not window_should_close():
        begin_drawing()
        clear_background(BLACK)
        
        frame = camera.get_frame()

        for face in face_detector.find_faces(frame, flip= True):
            for lms in face.landmarks:
                x, y, z = lms
                x = int(x * WIDTH)
                y = int(y * HEIGHT)
                draw_circle(x, y, 2, RED)

        end_drawing()
    close_window()
    camera.close()

    


if __name__ == "__main__":
    main()
