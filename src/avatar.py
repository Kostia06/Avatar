"""
Avatar system - draws an animated character based on face/hand landmarks
"""
import math

class Avatar:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.emotion = "neutral"  # neutral, happy, sad, excited
        self.action = None  # current gesture/action
        self.action_timer = 0
        self.action_duration = 30  # frames

    def set_emotion(self, face):
        """Determine emotion from face landmarks"""
        if face is None:
            self.emotion = "neutral"
            return

        # Simple emotion detection based on mouth shape
        lips = face.lips()
        if len(lips) > 0:
            # Calculate mouth openness
            mouth_top = min([lm[1] for lm in lips[:10]])
            mouth_bottom = max([lm[1] for lm in lips[10:20]])
            mouth_width = max([lm[0] for lm in lips]) - min([lm[0] for lm in lips])

            mouth_height = mouth_bottom - mouth_top
            mouth_ratio = mouth_height / max(mouth_width, 0.001)

            if mouth_ratio > 0.3:
                self.emotion = "happy"
            else:
                self.emotion = "neutral"

    def set_action(self, gesture):
        """Set avatar action based on detected gesture"""
        if gesture:
            self.action = gesture
            self.action_timer = self.action_duration

        if self.action_timer > 0:
            self.action_timer -= 1
        else:
            self.action = None

    def get_head_position(self, face):
        """Get head center position from face landmarks"""
        if face is None or len(face.landmarks) == 0:
            return (self.width // 2, self.height // 3)

        # Average of face landmarks for center
        face_oval = face.face_oval()
        if not face_oval:
            return (self.width // 2, self.height // 3)

        x = sum([lm[0] for lm in face_oval]) / len(face_oval) * self.width
        y = sum([lm[1] for lm in face_oval]) / len(face_oval) * self.height
        return (int(x), int(y))

    def get_head_size(self, face):
        """Calculate head size from face landmarks"""
        if face is None or len(face.landmarks) == 0:
            return 60

        face_oval = face.face_oval()
        if not face_oval:
            return 60

        x_coords = [lm[0] for lm in face_oval]
        y_coords = [lm[1] for lm in face_oval]

        width = (max(x_coords) - min(x_coords)) * self.width
        height = (max(y_coords) - min(y_coords)) * self.height

        return int(max(width, height) / 2)

    def draw(self, surface, face, hands, draw_circle, draw_line, draw_rect, COLOR_AVATAR):
        """Draw the avatar character"""
        import pygame

        head_pos = self.get_head_position(face)
        head_size = self.get_head_size(face)

        # Draw head
        head_color = self.get_emotion_color()
        draw_circle(surface, head_pos[0], head_pos[1], head_size, head_color)

        # Draw eyes
        eye_left_x = head_pos[0] - head_size // 3
        eye_right_x = head_pos[0] + head_size // 3
        eye_y = head_pos[1] - head_size // 4
        eye_size = 8

        # Eyes change based on emotion
        if self.emotion == "happy":
            # Closed happy eyes (curves)
            draw_circle(surface, eye_left_x, eye_y, eye_size, (50, 50, 50))
            draw_circle(surface, eye_right_x, eye_y, eye_size, (50, 50, 50))
        else:
            # Open eyes
            draw_circle(surface, eye_left_x, eye_y, eye_size, (255, 255, 255))
            draw_circle(surface, eye_right_x, eye_y, eye_size, (255, 255, 255))
            # Pupils
            draw_circle(surface, eye_left_x, eye_y, 4, (0, 0, 0))
            draw_circle(surface, eye_right_x, eye_y, 4, (0, 0, 0))

        # Draw mouth based on emotion
        mouth_y = head_pos[1] + head_size // 3
        mouth_width = head_size // 2
        mouth_height = 8

        if self.emotion == "happy":
            # Smile
            pygame.draw.arc(surface, (255, 100, 100),
                           (head_pos[0] - mouth_width, mouth_y, mouth_width * 2, mouth_height),
                           0, math.pi, 3)
        else:
            # Straight line mouth
            draw_line(surface, head_pos[0] - mouth_width // 2, mouth_y,
                     head_pos[0] + mouth_width // 2, mouth_y, (100, 100, 100))

        # Draw body
        body_top = head_pos[1] + head_size
        body_height = head_size
        body_width = head_size // 2

        draw_rect(surface, head_pos[0] - body_width // 2, body_top, body_width, body_height, COLOR_AVATAR)

        # Draw arms based on hands
        arm_length = head_size
        left_arm_pos = self.get_hand_position(hands, "Left") if hands else None
        right_arm_pos = self.get_hand_position(hands, "Right") if hands else None

        # Left arm
        if left_arm_pos:
            draw_line(surface, head_pos[0] - body_width // 2, body_top,
                     int(left_arm_pos[0]), int(left_arm_pos[1]), (200, 150, 100))
        else:
            draw_line(surface, head_pos[0] - body_width // 2, body_top,
                     head_pos[0] - body_width // 2 - arm_length, body_top, (200, 150, 100))

        # Right arm
        if right_arm_pos:
            draw_line(surface, head_pos[0] + body_width // 2, body_top,
                     int(right_arm_pos[0]), int(right_arm_pos[1]), (200, 150, 100))
        else:
            draw_line(surface, head_pos[0] + body_width // 2, body_top,
                     head_pos[0] + body_width // 2 + arm_length, body_top, (200, 150, 100))

        # Draw legs
        leg_length = head_size
        draw_line(surface, head_pos[0] - body_width // 4, body_top + body_height,
                 head_pos[0] - body_width // 4, body_top + body_height + leg_length, (150, 150, 200))
        draw_line(surface, head_pos[0] + body_width // 4, body_top + body_height,
                 head_pos[0] + body_width // 4, body_top + body_height + leg_length, (150, 150, 200))

        # Draw action indicator
        if self.action:
            self.draw_action_indicator(surface, head_pos, head_size, draw_circle)

    def get_emotion_color(self):
        """Get color based on emotion"""
        if self.emotion == "happy":
            return (255, 200, 100)  # Warm yellow
        elif self.emotion == "sad":
            return (100, 150, 255)  # Blue
        elif self.emotion == "excited":
            return (255, 100, 200)  # Pink
        else:
            return (200, 200, 200)  # Gray

    def get_hand_position(self, hands, hand_type):
        """Get hand palm position"""
        for hand in hands:
            if hand.hand_type == hand_type:
                palm_center = hand.palm()
                if palm_center:
                    x = sum([lm[0] for lm in palm_center]) / len(palm_center) * self.width
                    y = sum([lm[1] for lm in palm_center]) / len(palm_center) * self.height
                    return (x, y)
        return None

    def draw_action_indicator(self, surface, head_pos, head_size, draw_circle):
        """Draw action indicator above avatar head"""
        indicator_y = head_pos[1] - head_size - 20

        if self.action == "peace":
            draw_circle(surface, head_pos[0], indicator_y, 15, (255, 255, 0))  # Yellow
        elif self.action == "thumbs_up":
            draw_circle(surface, head_pos[0], indicator_y, 15, (0, 255, 0))   # Green
        elif self.action == "thumbs_down":
            draw_circle(surface, head_pos[0], indicator_y, 15, (255, 0, 0))   # Red
        elif self.action == "pointing":
            draw_circle(surface, head_pos[0], indicator_y, 15, (255, 150, 0)) # Orange
        elif self.action == "open_hand":
            draw_circle(surface, head_pos[0], indicator_y, 15, (100, 200, 255)) # Light blue
        elif self.action == "closed_fist":
            draw_circle(surface, head_pos[0], indicator_y, 15, (139, 69, 19))  # Brown
