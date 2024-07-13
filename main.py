from pyray import *
import sys

from src.hand import HandDetector
from src.face import FaceDetector
from src.camera import Camera

WIDTH = HEIGHT = 800


def main():
    init_window(WIDTH, HEIGHT, "Avatar")
    camera = Camera()
    hand_detector = HandDetector()
    face_detector = FaceDetector()
    while not window_should_close():
        begin_drawing()
        clear_background(BLACK)
        
        frame = camera.get_frame()
        for hand in hand_detector.find_hands(frame, flip = True):
            for lm in hand.landmarks:
                x, y = int(lm['x'] * WIDTH), int(lm['y'] * HEIGHT)
                draw_circle(x, y, 10, RED)
        for face in face_detector.find_faces(frame, flip = True):    
            for lm in face.landmarks:
                x, y = int(lm['x'] * WIDTH), int(lm['y'] * HEIGHT)
                draw_circle(x, y, 2, GREEN)
    

        end_drawing()
    close_window()
    camera.close()

    


if __name__ == "__main__":
    main()
