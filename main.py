import pygame
import pygame.gfxdraw
import sys
import os
import math

from src.hand import HandDetector
from src.face import FaceDetector
from src.camera import Camera
from src.smooth_renderer import SmoothRenderer

WIDTH = HEIGHT = 800

# Anti-aliasing for smoother rendering
def enable_antialiasing(surface):
    """Enable anti-aliasing for smoother shapes"""
    pass  # pygame.gfxdraw provides anti-aliased primitives

# Color definitions (RGB tuples)
COLOR_FACE = (200, 150, 100)      # Beige for face
COLOR_LEFT_EYE = (100, 200, 255)  # Light blue
COLOR_RIGHT_EYE = (100, 200, 255) # Light blue
COLOR_EYEBROW = (139, 69, 19)     # Brown
COLOR_NOSE = (255, 150, 100)      # Light coral
COLOR_LIPS = (255, 100, 150)      # Pink
COLOR_IRIS = (50, 50, 50)         # Dark gray
COLOR_HAND_PALM = (200, 150, 100) # Beige
COLOR_HAND_FINGER = (150, 200, 255) # Light blue
COLOR_FINGER_TIPS = (255, 200, 0) # Gold for finger tips
COLOR_BG = (0, 0, 0)               # Black background

def draw_landmarks(surface, landmarks, color, size=3):
    """Draw a set of landmarks as circles"""
    for lm in landmarks:
        x, y, z = lm
        x = int(x * WIDTH)
        y = int(y * HEIGHT)
        pygame.draw.circle(surface, color, (x, y), size)

def draw_connected_landmarks(surface, landmarks, color, size=2):
    """Draw landmarks connected by lines"""
    if len(landmarks) < 2:
        return

    for i in range(len(landmarks) - 1):
        x1, y1, z1 = landmarks[i]
        x2, y2, z2 = landmarks[i + 1]
        x1, y1 = int(x1 * WIDTH), int(y1 * HEIGHT)
        x2, y2 = int(x2 * WIDTH), int(y2 * HEIGHT)
        pygame.draw.line(surface, color, (x1, y1), (x2, y2), 2)

    # Draw circles at endpoints
    for lm in landmarks:
        x, y, z = lm
        x = int(x * WIDTH)
        y = int(y * HEIGHT)
        pygame.draw.circle(surface, color, (x, y), size)

def draw_face(surface, face):
    """Draw ultra-smooth face with proper depth and rotation handling"""
    if not face or not face.landmarks:
        return

    # Colors
    skin_base = (245, 220, 200)
    skin_shadow = (225, 195, 175)
    hair_color = (60, 40, 25)
    eyebrow_color = (65, 42, 26)
    tongue_color = (220, 110, 120)

    # Get face orientation for proper rendering
    nose = face.nose()
    face_turned = 0
    if len(nose) >= 5:
        # Calculate face rotation based on nose position
        nose_tip = nose[4]
        nose_center = nose[0]
        face_turned = (nose_tip[0] - nose_center[0]) * 100  # -100 to 100 scale

    # Get smooth face oval
    face_oval = face.face_oval()
    face_oval_points = []
    for i, lm in enumerate(face_oval):
        x, y = int(lm[0] * WIDTH), int(lm[1] * HEIGHT)
        # Apply smoothing based on rotation
        if abs(face_turned) > 20:
            # Adjust points to prevent distortion during rotation
            x += int(face_turned * 0.2 * (i / len(face_oval) - 0.5))
        face_oval_points.append((x, y))

    if len(face_oval_points) < 3:
        return

    # Calculate face bounds
    face_x_coords = [p[0] for p in face_oval_points]
    face_y_coords = [p[1] for p in face_oval_points]
    min_x, max_x = min(face_x_coords), max(face_x_coords)
    min_y, max_y = min(face_y_coords), max(face_y_coords)
    face_width = max_x - min_x
    face_height = max_y - min_y
    face_center_x = (min_x + max_x) / 2

    # Draw hair with rotation adjustment
    hair_top = min_y - face_height * 0.25
    hair_width = face_width * 1.3

    # Adjust hair position based on face rotation
    hair_offset = face_turned * 0.5

    # Anti-aliased hair
    hair_rect = pygame.Rect(
        int(face_center_x - hair_width / 2 + hair_offset),
        int(hair_top),
        int(hair_width),
        int(face_height * 0.9)
    )

    # Draw smooth hair with gfxdraw
    pygame.gfxdraw.filled_ellipse(surface,
                                  int(face_center_x + hair_offset),
                                  int(min_y),
                                  int(hair_width // 2),
                                  int(face_height * 0.45),
                                  hair_color)

    # Draw smooth face oval
    pygame.gfxdraw.aapolygon(surface, face_oval_points, skin_shadow)
    pygame.gfxdraw.filled_polygon(surface, face_oval_points, skin_base)
    pygame.gfxdraw.aapolygon(surface, face_oval_points, skin_shadow)

    # Draw smooth 3D nose
    nose_lms = face.nose()
    if len(nose_lms) >= 5:
        nose_tip = nose_lms[4]
        nose_bridge_top = nose_lms[0]
        nose_left = nose_lms[2]
        nose_right = nose_lms[3]

        nose_tip_x, nose_tip_y = int(nose_tip[0] * WIDTH), int(nose_tip[1] * HEIGHT)
        bridge_x, bridge_y = int(nose_bridge_top[0] * WIDTH), int(nose_bridge_top[1] * HEIGHT)
        left_x, left_y = int(nose_left[0] * WIDTH), int(nose_left[1] * HEIGHT)
        right_x, right_y = int(nose_right[0] * WIDTH), int(nose_right[1] * HEIGHT)

        # Draw smooth nose shape
        nose_shadow_poly = [(bridge_x - 4, bridge_y), (left_x, left_y),
                           (nose_tip_x, nose_tip_y + 2), (right_x, right_y), (bridge_x + 4, bridge_y)]

        pygame.gfxdraw.aapolygon(surface, nose_shadow_poly, (230, 200, 180))
        pygame.gfxdraw.filled_polygon(surface, nose_shadow_poly, (235, 205, 185))

        # Smooth nose tip highlight
        pygame.gfxdraw.aacircle(surface, nose_tip_x, nose_tip_y, 5, (255, 240, 230))
        pygame.gfxdraw.filled_circle(surface, nose_tip_x, nose_tip_y, 5, (255, 240, 230))

        # Smooth nostrils
        pygame.gfxdraw.aacircle(surface, left_x, left_y, 2, (200, 170, 150))
        pygame.gfxdraw.filled_circle(surface, left_x, left_y, 2, (200, 170, 150))
        pygame.gfxdraw.aacircle(surface, right_x, right_y, 2, (200, 170, 150))
        pygame.gfxdraw.filled_circle(surface, right_x, right_y, 2, (200, 170, 150))

    # Draw better eyebrows with thickness and taper
    left_eyebrow = face.left_eyebrow()
    right_eyebrow = face.right_eyebrow()

    # Left eyebrow with gradient thickness
    for i in range(len(left_eyebrow) - 1):
        x1, y1, z1 = left_eyebrow[i]
        x2, y2, z2 = left_eyebrow[i + 1]
        x1, y1 = int(x1 * WIDTH), int(y1 * HEIGHT)
        x2, y2 = int(x2 * WIDTH), int(y2 * HEIGHT)
        # Thickness decreases from inner to outer brow
        thickness = 6 - int(i * 0.4)
        thickness = max(thickness, 2)
        pygame.draw.line(surface, eyebrow_color, (x1, y1), (x2, y2), thickness)

    # Right eyebrow with gradient thickness
    for i in range(len(right_eyebrow) - 1):
        x1, y1, z1 = right_eyebrow[i]
        x2, y2, z2 = right_eyebrow[i + 1]
        x1, y1 = int(x1 * WIDTH), int(y1 * HEIGHT)
        x2, y2 = int(x2 * WIDTH), int(y2 * HEIGHT)
        thickness = 6 - int(i * 0.4)
        thickness = max(thickness, 2)
        pygame.draw.line(surface, eyebrow_color, (x1, y1), (x2, y2), thickness)

    # Detect real-time blinking from eye landmarks
    left_eye_points = [(int(lm[0] * WIDTH), int(lm[1] * HEIGHT)) for lm in face.left_eye()]
    right_eye_points = [(int(lm[0] * WIDTH), int(lm[1] * HEIGHT)) for lm in face.right_eye()]

    # Calculate eye openness (vertical distance)
    is_blinking = False
    if len(left_eye_points) >= 12 and len(right_eye_points) >= 12:
        # Left eye vertical distance
        left_top = left_eye_points[4]
        left_bottom = left_eye_points[12]
        left_eye_open = abs(left_top[1] - left_bottom[1])

        # Right eye vertical distance
        right_top = right_eye_points[4]
        right_bottom = right_eye_points[12]
        right_eye_open = abs(right_top[1] - right_bottom[1])

        # If eyes are less than 30% open, consider it a blink
        avg_eye_open = (left_eye_open + right_eye_open) / 2
        if avg_eye_open < 8:  # Threshold for closed eyes
            is_blinking = True

    # Draw eyes based on blink state
    if is_blinking:
        # Draw closed eyes (just lines)
        if len(left_eye_points) >= 4:
            pygame.draw.line(surface, (100, 70, 50), left_eye_points[0], left_eye_points[8], 3)
        if len(right_eye_points) >= 4:
            pygame.draw.line(surface, (100, 70, 50), right_eye_points[0], right_eye_points[8], 3)
    else:
        # Draw open eyes with white sclera
        if len(left_eye_points) > 2:
            pygame.draw.polygon(surface, (255, 255, 255), left_eye_points)
            pygame.draw.polygon(surface, (200, 200, 200), left_eye_points, 1)

        if len(right_eye_points) > 2:
            pygame.draw.polygon(surface, (255, 255, 255), right_eye_points)
            pygame.draw.polygon(surface, (200, 200, 200), right_eye_points, 1)

        # Draw iris with gradient
        left_iris_lms = face.left_iris()
        right_iris_lms = face.right_iris()

        if left_iris_lms:
            iris_x = sum(lm[0] for lm in left_iris_lms) / len(left_iris_lms) * WIDTH
            iris_y = sum(lm[1] for lm in left_iris_lms) / len(left_iris_lms) * HEIGHT
            pygame.draw.circle(surface, (70, 130, 180), (int(iris_x), int(iris_y)), 12)
            pygame.draw.circle(surface, (20, 20, 20), (int(iris_x), int(iris_y)), 6)
            pygame.draw.circle(surface, (255, 255, 255), (int(iris_x - 2), int(iris_y - 2)), 2)

        if right_iris_lms:
            iris_x = sum(lm[0] for lm in right_iris_lms) / len(right_iris_lms) * WIDTH
            iris_y = sum(lm[1] for lm in right_iris_lms) / len(right_iris_lms) * HEIGHT
            pygame.draw.circle(surface, (70, 130, 180), (int(iris_x), int(iris_y)), 12)
            pygame.draw.circle(surface, (20, 20, 20), (int(iris_x), int(iris_y)), 6)
            pygame.draw.circle(surface, (255, 255, 255), (int(iris_x - 2), int(iris_y - 2)), 2)

    # Draw lips with mouth opening detection
    lips_points = [(int(lm[0] * WIDTH), int(lm[1] * HEIGHT)) for lm in face.lips()]

    # Detect mouth opening
    mouth_open = False
    if len(lips_points) >= 20:
        # Calculate mouth vertical opening
        upper_lip_center_y = sum(p[1] for p in lips_points[:10]) / 10
        lower_lip_center_y = sum(p[1] for p in lips_points[10:20]) / 10
        mouth_opening = abs(lower_lip_center_y - upper_lip_center_y)

        if mouth_opening > 15:  # Threshold for open mouth
            mouth_open = True

            # Draw tongue when mouth is open
            mouth_center_x = sum(p[0] for p in lips_points[:20]) / 20
            mouth_center_y = (upper_lip_center_y + lower_lip_center_y) / 2

            # Tongue shape (ellipse)
            tongue_width = 20
            tongue_height = 25
            tongue_rect = pygame.Rect(
                int(mouth_center_x - tongue_width / 2),
                int(mouth_center_y),
                tongue_width,
                tongue_height
            )
            pygame.draw.ellipse(surface, tongue_color, tongue_rect)
            pygame.draw.ellipse(surface, (180, 90, 100), tongue_rect, 2)

            # Tongue line detail
            pygame.draw.line(surface, (180, 90, 100),
                           (int(mouth_center_x), int(mouth_center_y + 5)),
                           (int(mouth_center_x), int(mouth_center_y + tongue_height - 5)), 1)

    # Draw lips
    if len(lips_points) >= 20:
        upper_lip = lips_points[:20]
        pygame.draw.polygon(surface, (200, 100, 120), upper_lip)
        pygame.draw.polygon(surface, (180, 80, 100), upper_lip, 1)

        lower_lip = lips_points[10:30] if len(lips_points) >= 30 else lips_points[10:]
        pygame.draw.polygon(surface, (220, 120, 140), lower_lip)
        pygame.draw.polygon(surface, (200, 100, 120), lower_lip, 1)

        # Lip gloss
        if len(lower_lip) > 5:
            highlight_x = sum(p[0] for p in lower_lip[:5]) / 5
            highlight_y = sum(p[1] for p in lower_lip[:5]) / 5
            pygame.draw.circle(surface, (255, 200, 220), (int(highlight_x), int(highlight_y)), 3)

def draw_hand(surface, hand):
    """Draw ultra-smooth hand with anti-aliasing and proper depth"""
    import math

    # Realistic skin tone colors
    skin_base = (235, 200, 178)
    skin_dark = (215, 175, 155)
    skin_light = (245, 220, 200)
    nail_color = (255, 240, 245)
    nail_outline = (230, 200, 210)

    # Get hand z-coordinate for depth adjustment
    avg_z = sum(lm[2] for lm in hand.landmarks) / len(hand.landmarks)
    depth_scale = 1 + avg_z * 0.5  # Scale based on depth

    # Draw smooth palm
    palm_lms = hand.palm()
    if palm_lms and len(palm_lms) > 2:
        palm_points = [(int(lm[0] * WIDTH), int(lm[1] * HEIGHT)) for lm in palm_lms]

        # Anti-aliased palm
        pygame.gfxdraw.aapolygon(surface, palm_points, skin_dark)
        pygame.gfxdraw.filled_polygon(surface, palm_points, skin_base)

    # Draw each finger with smooth anti-aliasing
    fingers = hand.fingers()

    for finger_idx, finger in enumerate(fingers):
        if len(finger) < 2:
            continue

        # Draw smooth finger segments
        finger_points = []
        for i, joint in enumerate(finger):
            x, y, z = joint
            x, y = int(x * WIDTH), int(y * HEIGHT)
            finger_points.append((x, y))

            # Draw smooth joint circles
            base_radius = (14 if finger_idx == 0 else 12) * depth_scale
            radius = int(base_radius - (i * 2))
            radius = max(radius, 4)

            # Anti-aliased circles at joints
            pygame.gfxdraw.aacircle(surface, x, y, radius, skin_light)
            pygame.gfxdraw.filled_circle(surface, x, y, radius, skin_light)

        # Draw smooth connections between joints
        for i in range(len(finger_points) - 1):
            x1, y1 = finger_points[i]
            x2, y2 = finger_points[i + 1]

            # Calculate smooth width
            width = int((12 - i * 2) * depth_scale)
            width = max(width, 4)

            # Draw thick anti-aliased line
            angle = math.atan2(y2 - y1, x2 - x1)
            dx = int(math.sin(angle) * width)
            dy = int(math.cos(angle) * width)

            poly = [(x1 - dx, y1 + dy), (x1 + dx, y1 - dy),
                   (x2 + dx, y2 - dy), (x2 - dx, y2 + dy)]

            pygame.gfxdraw.aapolygon(surface, poly, skin_light)
            pygame.gfxdraw.filled_polygon(surface, poly, skin_light)

    # Draw smooth nails
    finger_tips = hand.finger_tips()
    for i, tip in enumerate(finger_tips):
        x, y, z = tip
        x, y = int(x * WIDTH), int(y * HEIGHT)

        # Scale nail size with depth
        nail_width = int(11 * depth_scale)
        nail_height = int(9 * depth_scale)

        # Draw smooth nail
        pygame.gfxdraw.aaellipse(surface, x, y, nail_width // 2, nail_height // 2, nail_outline)
        pygame.gfxdraw.filled_ellipse(surface, x, y, nail_width // 2, nail_height // 2, nail_color)

        # Smooth nail highlight
        pygame.gfxdraw.filled_ellipse(surface, x - 2, y - 2, 2, 1, (255, 255, 255))

def main():
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Avatar - Ultra Smooth")
    clock = pygame.time.Clock()

    camera = Camera()
    hand_detector = HandDetector()
    face_detector = FaceDetector()
    renderer = SmoothRenderer(WIDTH, HEIGHT)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(COLOR_BG)
        frame = camera.get_frame()

        if frame is not None:
            faces = face_detector.find_faces(frame, flip=True)
            hands = hand_detector.find_hands(frame, flip=True)

            # Get first face (if exists)
            current_face = faces[0] if faces else None

            # Calculate depth order for proper layering
            elements = renderer.calculate_depth_order(current_face, hands)

            # Draw elements in depth order (back to front)
            for element_type, element, depth in elements:
                if element_type == 'face':
                    draw_face(screen, element)
                elif element_type == 'hand':
                    draw_hand(screen, element)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    camera.close()

if __name__ == "__main__":
    main()
