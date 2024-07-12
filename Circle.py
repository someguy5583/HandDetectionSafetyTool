import json
import math

import cv2
from . import Shape

from . import tracking


class Circle(Shape.Shape):
    def __init__(self, positions: list, color=(255, 0, 0), template=None, name:str="Circle"):
        self.positions = positions
        self.center = self.positions[0]
        self.radius = int(math.sqrt(
            (self.center[0] - self.positions[1][0]) ** 2 +
            (self.center[1] - self.positions[1][1]) ** 2
        ))
        self.template = template

        self.color = color
        self.name = name

    def find_template(self, frame):
        cropped_image = frame[self.center[1]:self.positions[1][1],
                              self.center[0]:self.positions[1][0]]
        self.template = cropped_image
        return cropped_image

    def save(self, name: str, frame):
        start = [self.center[0]-self.radius, self.center[1]-self.radius]
        end = [self.center[0]+self.radius, self.center[1]+self.radius]
        cropped_image = frame[start[1]:end[1],
                              start[0]:end[0]]
        self.template = cropped_image
        cv2.imwrite(name, cropped_image)

    def set_positions(self, positions: list):
        self.positions = positions
        self.center = self.positions[0]
        self.radius = int(math.sqrt(
            (self.center[0] - self.positions[1][0]) ** 2 +
            (self.center[1] - self.positions[1][1]) ** 2
        ))

    def get_positions(self):
        return self.positions

    def track(self, frame):
        if self.template is None: return

        track = tracking.detect_marker(frame, self.template)
        self.set_positions(track if track is not None else self.positions)

    def render(self, frame, thickness, index, shouldDisplayIndex):
        cv2.circle(frame, self.center, self.radius, self.color, thickness)
        if shouldDisplayIndex:
            cv2.putText(frame, f"{index}", self.positions[0], cv2.FONT_HERSHEY_PLAIN, 3, self.color, thickness)

    def check_point(self, x, y) -> bool:
        if math.sqrt((self.positions[0][0] - x) ** 2 + (self.positions[0][1] - y) ** 2) < self.radius:
            return True
        return False

    def __str__(self):
        return "Circle|"+json.dumps(self.positions)
