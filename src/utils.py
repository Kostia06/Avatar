import math


def rotate_x(points, angle):
    for point in points:
        y = point['y']
        z = point['z']
        point['y'] = y * math.cos(angle) - z * math.sin(angle)
        point['z'] = y * math.sin(angle) + z * math.cos(angle)
    return points

def rotate_y(points, angle):
    for point in points:
        x = point['x']
        z = point['z']
        point['x'] = x * math.cos(angle) - z * math.sin(angle)
        point['z'] = x * math.sin(angle) + z * math.cos(angle)
    return points

def rotate_z(points, angle):
    for point in points:
        x = point['x']
        y = point['y']
        point['x'] = x * math.cos(angle) - y * math.sin(angle)
        point['y'] = x * math.sin(angle) + y * math.cos(angle)
    return points

