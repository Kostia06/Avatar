"""
Gesture detection for hand landmarks
"""

def is_peace_sign(hand):
    """Detect peace sign: index and middle fingers up, others down"""
    fingers_up = [hand.finger_up(i) for i in range(5)]  # thumb, index, middle, ring, pinky
    # Peace: index and middle up, thumb down or neutral, ring and pinky down
    return fingers_up[1] and fingers_up[2] and not fingers_up[3] and not fingers_up[4]

def is_thumbs_up(hand):
    """Detect thumbs up: thumb pointing up, other fingers closed"""
    fingers_up = [hand.finger_up(i) for i in range(5)]
    # Thumbs up: only thumb up
    return fingers_up[0] and not fingers_up[1] and not fingers_up[2] and not fingers_up[3] and not fingers_up[4]

def is_thumbs_down(hand):
    """Detect thumbs down: thumb pointing down, other fingers closed"""
    fingers_up = [hand.finger_up(i) for i in range(5)]
    thumb_tip = hand.finger_tips()[0]
    knuckle = hand.knuckles()[0]
    # Thumbs down: thumb down (y-coordinate check), all fingers closed
    thumb_down = thumb_tip[1] > knuckle[1]  # y increases downward
    return thumb_down and not fingers_up[1] and not fingers_up[2] and not fingers_up[3] and not fingers_up[4]

def is_pointing(hand):
    """Detect pointing: index finger up, middle finger down"""
    fingers_up = [hand.finger_up(i) for i in range(5)]
    # Pointing: index up, middle down
    return fingers_up[1] and not fingers_up[2] and not fingers_up[3] and not fingers_up[4]

def is_open_hand(hand):
    """Detect open hand: all fingers up"""
    fingers_up = [hand.finger_up(i) for i in range(5)]
    return all(fingers_up)

def is_closed_fist(hand):
    """Detect closed fist: all fingers down"""
    fingers_up = [hand.finger_up(i) for i in range(5)]
    return not any(fingers_up)

def detect_gesture(hand):
    """
    Detect gesture from hand landmarks.
    Returns gesture name or None if no recognizable gesture.
    """
    if is_peace_sign(hand):
        return "peace"
    elif is_thumbs_up(hand):
        return "thumbs_up"
    elif is_thumbs_down(hand):
        return "thumbs_down"
    elif is_pointing(hand):
        return "pointing"
    elif is_open_hand(hand):
        return "open_hand"
    elif is_closed_fist(hand):
        return "closed_fist"
    return None
