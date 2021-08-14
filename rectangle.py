from point import Point
import numpy as np
from numpy import linalg


class Rectangle:

    OFFSET = 1

    def __init__(self, lower_left: Point, upper_right: Point):
        # Lower Left to Upper Right
        self.lower_left = lower_left
        self.upper_right = upper_right
        self.width, self.height, self.area = self.calculate_properties()

    # CALCULATED THE WIDTH, HEIGHT AND AREA OF THE RECTANGLE
    def calculate_properties(self):
        """Calculates the width, height and area of self

        Returns:
            int -- returns the width height and area values
        """
        width = self.upper_right.x - self.lower_left.x
        height = self.upper_right.y - self.lower_left.y
        area = width*height
        return width, height, area

    # CHECK TO SEE IF SELF OVERLAPS WITH ANOTHER RECTANGLE
    def overlaps(self, rect: 'Rectangle'):
        # IS TO THE LEFT
        if self.lower_left.x > rect.upper_right.x:
            return False
        # IS ABOVE
        elif self.upper_right.y < rect.lower_left.y:
            return False
        # IS TO THE RIGHT
        elif self.upper_right.x < rect.lower_left.x:
            return False
        # IS UNDER
        elif self.lower_left.y > rect.upper_right.y:
            return False
        else:
            return True

    # CHECK TO SEE IF SELF CONTAIN THE RECTANGLE GIVEN AS A PARAMETER
    def contains(self, rect: 'Rectangle'):
        if (self.lower_left.x < rect.lower_left.x
            and self.lower_left.y < rect.lower_left.y
            and self.upper_right.x > rect.upper_right.x
                and self.upper_right.y > rect.upper_right.y):
            return True
        else:
            return False

    # EXPANDS SELF TO CONTAIN GIVEN RECTANGLE
    def expand_to_contain(self, rect: 'Rectangle'):
        if self.lower_left.x >= rect.lower_left.x:
            self.lower_left.x = rect.lower_left.x - self.OFFSET
        if self.lower_left.y >= rect.lower_left.y:
            self.lower_left.y = rect.lower_left.y - self.OFFSET
        if self.upper_right.x <= rect.upper_right.x:
            self.upper_right.x = rect.upper_right.x + self.OFFSET
        if self.upper_right.y <= rect.upper_right.y:
            self.upper_right.y = rect.upper_right.y + self.OFFSET
        self.calculate_properties()

    # CREATES ANOTHER RECTANGLE CLASS THAT CONTAINS GIVEN ENTRY
    @classmethod
    def create_mbr_for_entry(cls, rect: 'Rectangle'):
        lower_left = Point(rect.lower_left.x - 1, rect.lower_left.y - 1)
        upper_right = Point(rect.upper_right.x + 1, rect.upper_right.y + 1)
        return cls(lower_left, upper_right)

    # CALCULATES THE EXPANSION COST BY CALCULATING THE INCREASE IN AREA IF IT EXPANDED
    def expansion_area_cost(self, rect: 'Rectangle'):
        temp_rect = Rectangle(self.lower_left, self.upper_right)
        temp_rect.expand_to_contain(rect)
        _, _, temp_area = temp_rect.calculate_properties()
        return temp_area - self.area

    # CHECKS IF SELF DOMINATES A GIVEN RECTANGLE BY COMPARING ITS UPPER RIGHT CORNER WITH THE LOWER LEFT CORNER OF THE OTHER RECTANGLE
    def dominates_rec(self, rec: 'Rectangle'):
        if self.upper_right.dominates(rec.lower_left):
            return True
        else:
            return False

    # CHECKS IF SELF IS DOMINATED BY GIVEN RECTANGLE USING THE SAME COMPARISON AS ABOVE
    def is_dominated(self, rec: 'Rectangle'):
        if rec.upper_right.dominates(self.lower_left):
            return True
        else:
            return False

    # CALCULATES MINDIST OF RECTANGLE FROM (0, 0). USES LOWER LEFT CORNER ALWAYS
    def mindist(self, point: Point = Point(0, 0)):
        if point.x > self.lower_left.x and point.x < self.upper_right.x and point.y > self.lower_left.y and point.y < self.upper_right.y:
            return 0
        a = np.array([self.lower_left.x, self.lower_left.y])
        b = np.array([point.x, point.y])
        return np.linalg.norm((a-b), 1)

    def __repr__(self, level=0):
        ret = "LLx: " + str(self.lower_left.x) + " LLy: " + str(self.lower_left.y) + "\n" + \
            "\t"*level + "URx: " + \
            str(self.upper_right.x) + " URy: " + str(self.upper_right.y)
        return ret
