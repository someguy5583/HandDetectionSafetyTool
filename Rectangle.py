import json

import cv2

import Shape
import tracking


class Rectangle(Shape.Shape):
    def __init__(self, positions: list, color=(0, 0, 255), template=None):
        self.positions = positions
        self.template = template

        self.color = color

    def find_template(self, frame):
        cropped_image = frame[self.positions[0][1]:self.positions[1][1],
                              self.positions[0][0]:self.positions[1][0]]
        self.template = cropped_image
        return cropped_image

    def save(self, name: str, frame):
        cropped_image = frame[self.positions[0][1]:self.positions[1][1],
                              self.positions[0][0]:self.positions[1][0]]
        self.template = cropped_image
        cv2.imwrite(name, cropped_image)

    def set_positions(self, positions: list):
        self.positions = positions

    def get_positions(self):
        return self.positions

    def track(self, frame):
        if self.template is None: return

        track = tracking.detect_marker(frame, self.template)
        self.set_positions(track if track is not None else self.positions)

    def render(self, frame, thickness: int, index: int, shouldDisplayIndex: bool):
        cv2.rectangle(frame, self.positions[0], self.positions[1], self.color, thickness)
        if shouldDisplayIndex:
            cv2.putText(frame, f"{index}", self.positions[0],
                        cv2.FONT_HERSHEY_PLAIN, 3, self.color, thickness)

    def check_point(self, x, y) -> bool:
        if min(self.positions[0][0], self.positions[1][0]) <= x <= max(self.positions[0][0], self.positions[1][0]):
            if min(self.positions[0][1], self.positions[1][1]) <= y <= max(self.positions[0][1], self.positions[1][1]):
                return True
        return False

    def __str__(self):
        return "Rect|" + json.dumps(self.positions)
