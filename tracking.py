import cv2
import numpy as np


def detect_marker(frame, template):
    try:
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (3, 3), 0.5)
        # template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template = cv2.GaussianBlur(template, (3, 3), 0.5)

        # Perform template matching
        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)

        # Find the location with the maximum value
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val < 0.5:
            print("Image Couldn't be Found")
            return None
        # loc = np.sort()
        (top_x, top_y) = max_loc
        return [(int(np.average(top_x)), int(np.average(top_y))),
                (int(np.average(top_x)) + template.shape[1], int(np.average(top_y)) + template.shape[0])]
    except:
        return None