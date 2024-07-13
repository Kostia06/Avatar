import mediapipe as mp
import numpy as np
import cv2

_finger_tips = [4, 8, 12, 16, 20]
_fingers = [[4, 3, 2], [8, 7, 6, 5], [12,11, 10, 9], [16, 15, 14, 13], [20, 19, 18, 17]]
_palm = [0, 1, 2, 5, 9, 13, 17]
_knuckles = [2, 5, 9, 13, 17]


class Hand:
    def __init__(self, hand_type, landmarks):
        self.hand_type = hand_type
        self.landmarks = landmarks
    
    def finger_up(self, finger):
        if finger < 0 or finger > 4: return False
        finger_tip = self.landmarks[_finger_tips[finger]]
        knuckle = self.landmarks[_knuckles[finger]]
        return finger_tip[1] < knuckle[1]

    def palm(self):
        return [self.landmarks[i] for i in _palm]

    def knuckles(self):
        return [self.landmarks[i] for i in _knuckles]

    def finger_tips(self):
        return [self.landmarks[i] for i in _finger_tips]

    def fingers(self):
        return [[self.landmarks[i] for i in finger] for finger in _fingers]

class HandDetector:
    def __init__(self, image_mode = False, max_hands = 2, min_detection_confidence = 0.5, min_tracking_confidence = 0.5):
        mp_hands = mp.solutions.hands
        self.hands = mp_hands.Hands(
            static_image_mode = image_mode,
            max_num_hands = max_hands,
            min_detection_confidence = min_detection_confidence,
            min_tracking_confidence = min_tracking_confidence
        )

    def find_hands(self, frame, flip = False):
        found_hands = self.hands.process(frame)
        array_of_hands = []
        height, width, _ = frame.shape
        if not found_hands.multi_hand_landmarks:
            return array_of_hands
        for hand_type, hand_landmarks in zip(found_hands.multi_handedness, found_hands.multi_hand_landmarks):
            hand_landmarks = hand_landmarks.landmark
            hand_type = hand_type.classification[0].label
            if flip:
                hand_landmarks = [[1 - lm.x, lm.y, lm.z] for lm in hand_landmarks]
                if hand_type == 'Right':
                    hand_type = 'Left'
                else:
                    hand_type = 'Right'
            else:
                hand_landmarks = [[lm.x, lm.y, lm.z] for lm in hand_landmarks]
            hand = Hand(hand_type, hand_landmarks)
            array_of_hands.append(hand)
        return array_of_hands
        
