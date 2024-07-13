import mediapipe as mp
import numpy as np
import cv2

_face_outline = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
_forehead = [127, 162, 21, 54, 103, 67, 109, 10, 338, 297, 332, 284, 251, 389, 301, 298, 333, 299, 337, 151, 108, 69, 104, 68, 71, 139]
_hair = [301, 298, 333, 299, 337, 151, 108, 69, 104, 68, 71, 139]
_lip_inner = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
_lip_upper = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 320, 404, 315, 16, 85, 180, 90, 146]
_eyes = [468, 473]
_eye_left = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
_eye_right = [263, 466, 388, 387, 386, 385, 384, 398, 362, 382, 381, 380, 374, 373, 390, 249]
_brow_left = [55, 65, 52, 53, 46]
_brow_right = [285, 295, 282, 283, 276]
_iris_left = [468, 469, 470, 471, 472]
_iris_right = [473, 474, 475, 476, 477]


class Face:
    def __init__(self, landmarks):
        self.landmarks = landmarks
    def face_outline(self):
        return [self.landmarks[i] for i in _face_outline]
    def forehead(self):
        return [self.landmarks[i] for i in _forehead]
    def hair(self):
        return [self.landmarks[i] for i in _hair]
    def lip_inner(self):
        return [self.landmarks[i] for i in _lip_inner]
    def lip_upper(self):
        return [self.landmarks[i] for i in _lip_upper]
    def eyes(self):
        return [self.landmarks[i] for i in _eyes]
    def eye_left(self):
        return [self.landmarks[i] for i in _eye_left]
    def eye_right(self):
        return [self.landmarks[i] for i in _eye_right]
    def brow_left(self):
        return [self.landmarks[i] for i in _brow_left]
    def brow_right(self):
        return [self.landmarks[i] for i in _brow_right]
    def iris_left(self):
        return [self.landmarks[i] for i in _iris_left]
    def iris_right(self):
        return [self.landmarks[i] for i in _iris_right]
    

class FaceDetector:
    def __init__(self, image_mode = False, max_faces = 1, min_detection_confidence = 0.5, min_tracking_confidence = 0.5):
        mp_face = mp.solutions.face_mesh
        self.faces = mp_face.FaceMesh(
            static_image_mode = image_mode,
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
                landmarks = [{'x' :1 - lm.x,'y': lm.y,'z' : lm.z} for lm in landmarks]
            array_of_faces.append(Face(landmarks))
        return array_of_faces
