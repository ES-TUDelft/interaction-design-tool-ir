from es_common.enums.es_enum import ESEnum


class LedColor(ESEnum):
    RED = (1.0, 0.0, 0.0)
    GREEN = (0.0, 1.0, 0.0)
    BLUE = (0.0, 0.0, 1.0)
    WHITE = (1.0, 1.0, 1.0)

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
