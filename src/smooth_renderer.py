"""
Smooth renderer for avatar with anti-aliasing and proper depth handling
"""
import pygame
import pygame.gfxdraw
import math

class SmoothRenderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.prev_face_landmarks = None
        self.prev_hand_landmarks = []

    def smooth_point(self, current, previous, smoothing=0.3):
        """Smooth movement between frames"""
        if previous is None:
            return current
        return (
            previous[0] + (current[0] - previous[0]) * smoothing,
            previous[1] + (current[1] - previous[1]) * smoothing,
            current[2] if len(current) > 2 else 0
        )

    def draw_antialiased_circle(self, surface, x, y, radius, color):
        """Draw anti-aliased circle for smoother edges"""
        pygame.gfxdraw.aacircle(surface, int(x), int(y), int(radius), color)
        pygame.gfxdraw.filled_circle(surface, int(x), int(y), int(radius), color)

    def draw_antialiased_polygon(self, surface, points, color):
        """Draw anti-aliased polygon"""
        if len(points) > 2:
            pygame.gfxdraw.aapolygon(surface, points, color)
            pygame.gfxdraw.filled_polygon(surface, points, color)

    def draw_thick_aaline(self, surface, x1, y1, x2, y2, color, thickness):
        """Draw thick anti-aliased line"""
        angle = math.atan2(y2 - y1, x2 - x1)
        dx = math.sin(angle) * thickness / 2
        dy = math.cos(angle) * thickness / 2

        points = [
            (int(x1 - dx), int(y1 + dy)),
            (int(x1 + dx), int(y1 - dy)),
            (int(x2 + dx), int(y2 - dy)),
            (int(x2 - dx), int(y2 + dy))
        ]
        self.draw_antialiased_polygon(surface, points, color)

    def get_face_orientation(self, face):
        """Detect face orientation (front, left, right)"""
        if not face or not face.landmarks:
            return 'front', 0

        # Get nose tip and center
        nose = face.nose()
        if len(nose) < 5:
            return 'front', 0

        nose_tip = nose[4]
        nose_bridge = nose[0]

        # Calculate horizontal offset
        offset_x = (nose_tip[0] - nose_bridge[0]) * self.width

        if offset_x > 30:
            return 'right', offset_x
        elif offset_x < -30:
            return 'left', offset_x
        else:
            return 'front', offset_x

    def calculate_depth_order(self, face, hands):
        """Calculate rendering order based on z-coordinates"""
        elements = []

        # Add face with average z-depth
        if face and face.landmarks:
            avg_z = sum(lm[2] for lm in face.landmarks) / len(face.landmarks)
            elements.append(('face', face, avg_z))

        # Add hands with their z-depths
        for hand in hands:
            avg_z = sum(lm[2] for lm in hand.landmarks) / len(hand.landmarks)
            elements.append(('hand', hand, avg_z))

        # Sort by z-depth (back to front)
        elements.sort(key=lambda x: x[2], reverse=True)

        return elements