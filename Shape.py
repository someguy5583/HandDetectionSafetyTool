import json


class Shape:
    def find_template(self, frame):
        pass

    def save(self, name: str, frame):
        pass

    @staticmethod
    def read(line: str):
        return json.loads(line)

    def set_positions(self, positions: list):
        pass

    def get_positions(self):
        pass

    def track(self, frame):
        pass

    def render(self, frame, thickness: int, index: int, shouldDisplayIndex: bool):
        pass

    def check_point(self, x, y):
        pass