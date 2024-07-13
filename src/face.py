import mediapipe as mp
import numpy as np
import cv2

_face_lips = [
    61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 185, 40, 39, 37, 0, 267, 269, 270, 409, 
    78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 191, 80, 81, 82, 13, 312, 311, 310, 415
]

_face_left_center_eye = 468

_face_left_eye = [ 263, 249, 390, 373, 374, 380, 381, 382, 362, 466, 388, 387, 386, 385, 384, 398]

_face_left_iris = [ 474, 475, 476, 477 ]

_face_left_eyebrow = [ 276, 283, 282, 295, 285, 300, 293, 334, 296, 336 ]

_face_right_center_eye = 473

_face_right_eye = [ 33, 7, 163, 144, 145, 153, 154, 155, 133, 246, 161, 160, 159, 158, 157, 173 ]

_face_right_iris = [ 469, 470, 471, 472 ]

_face_right_eyebrow = [ 46, 53, 52, 65, 55, 70, 63, 105, 66, 107 ]

_face_face_oval = [
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378,
    400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21,
    54, 103, 67, 109
]

_face_nose = [
    168, 6, 197, 195, 5, 4, 1, 19, 94, 2, 98, 97, 326, 327, 294, 278, 344, 440,
    275, 45, 220, 115, 48, 64
]

class Face:
    def __init__(self, landmarks):
        self.landmarks = landmarks
    def lips(self):
        return [self.landmarks[i] for i in _face_lips]
    def left_center_eye(self):
        return self.landmarks[_face_left_center_eye]
    def left_eye(self):
        return [self.landmarks[i] for i in _face_left_eye]
    def left_iris(self):
        return [self.landmarks[i] for i in _face_left_iris]
    def left_eyebrow(self):
        return [self.landmarks[i] for i in _face_left_eyebrow]
    def right_center_eye(self):
        return self.landmarks[_face_right_center_eye]
    def right_eye(self):
        return [self.landmarks[i] for i in _face_right_eye]
    def right_iris(self):
        return [self.landmarks[i] for i in _face_right_iris]
    def right_eyebrow(self):
        return [self.landmarks[i] for i in _face_right_eyebrow]
    def face_oval(self):
        return [self.landmarks[i] for i in _face_face_oval]
    def nose(self):
        return [self.landmarks[i] for i in _face_nose]

class FaceDetector:
    def __init__(self, image_mode = False, max_faces = 1, min_detection_confidence = 0.5, min_tracking_confidence = 0.5):
        mp_face = mp.solutions.face_mesh
        self.faces = mp_face.FaceMesh(
            static_image_mode = image_mode,
            refine_landmarks = True,
            max_num_faces = max_faces,
            min_detection_confidence = min_detection_confidence,
            min_tracking_confidence = min_tracking_confidence
        )

    def find_faces(self, frame, flip = False):
        found_faces = self.faces.process(frame)
        array_of_faces = []
        if not found_faces.multi_face_landmarks:
            return array_of_faces
        for landmarks in found_faces.multi_face_landmarks:
            landmarks = landmarks.landmark
            if flip:
                landmarks = [[1 - lm.x, lm.y, lm.z] for lm in landmarks]
            else:
                landmarks = [[lm.x, lm.y, lm.z] for lm in landmarks]
            array_of_faces.append(Face(landmarks))
        return array_of_faces
