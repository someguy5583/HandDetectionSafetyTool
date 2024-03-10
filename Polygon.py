import json

import cv2
import numpy as np

import Shape
import tracking

import shapely.geometry


class Polygon(Shape.Shape):
    def __init__(self, positions: list, color=(0, 0, 255), template=None):
        self.max_values = None
        self.min_values = None
        self.positions = positions
        self.shapely_positions = [(x[0], x[1]) for x in self.positions]
        self.color = color
        self.template = template

    def set_min_max(self):
        numpy_array = np.array(self.positions)

        # Find the max/min values in each column
        self.max_values = np.amax(numpy_array, axis=0)
        self.min_values = np.amin(numpy_array, axis=0)
        print(self.min_values)
        print(self.max_values)

    def find_template(self, frame):
        self.set_min_max()
        cropped_image = frame[self.min_values[1]:self.max_values[1],
                              self.min_values[0]:self.max_values[0]]

        self.template = cropped_image
        return cropped_image

    def save(self, name: str, frame):
        self.find_template(frame)
        cv2.imwrite(name, self.template)

    def add_position(self, pos: list):
        self.positions.append(pos)
        self.shapely_positions = [(x[0], x[1]) for x in self.positions]

    def del_position(self, i: int):
        self.positions.pop(i)
        self.shapely_positions = [(x[0], x[1]) for x in self.positions]

    def set_positions(self, positions: list):
        self.positions = positions
        self.shapely_positions = [(x[0], x[1]) for x in self.positions]

    def get_positions(self):
        return self.positions

    def track(self, frame):
        if self.template is None:
            return

        track = tracking.detect_marker(frame, self.template)
        if track is None:
            return

        self.set_min_max()
        track = np.array(track)
        max_v = np.amax(track, axis=0)

        dx = max_v[0] - self.max_values[0]
        dy = max_v[1] - self.max_values[1]

        for i in range(len(self.positions)):
            self.positions[i][0] += dx
            self.positions[i][1] += dy

        self.shapely_positions = [(x[0], x[1]) for x in self.positions]

    def render(self, frame, thickness: int, index: int, should_display_index: bool):
        if len(self.positions) == 0:
            return

        for i in range(len(self.positions) - 1):
            cv2.line(frame, self.positions[i], self.positions[i + 1],
                     self.color, thickness)

        # closing the shape
        cv2.line(frame, self.positions[-1], self.positions[0],
                 self.color, thickness)

        if should_display_index:
            cv2.putText(frame, f"{index}", self.positions[0],
                        cv2.FONT_HERSHEY_PLAIN, 3, self.color, thickness)

    def check_point(self, x, y):
        p = shapely.geometry.Point(x, y)
        shape = shapely.geometry.Polygon(self.shapely_positions)

        return p.within(shape)

    def __str__(self):
        for i in range(len(self.positions)):
            self.positions[i] = [int(self.positions[i][0]), int(self.positions[i][1])]
        return "Poly|" + json.dumps(self.positions)
