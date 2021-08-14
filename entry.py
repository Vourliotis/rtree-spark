from rectangle import Rectangle, Point


class Entry:
    # An entry for the R-Tree
    def __init__(self, letter: str, mbr: Rectangle):
        self.letter = letter
        self.mbr: Rectangle = mbr

    # CALCULATES THE MINDIST TO (0, 0) OF THE LOWER LEFT POINT OF ITS MBR
    def mindist(self, point: Point = Point(0, 0)):
        return self.mbr.mindist(point)

    def __repr__(self, level=0):
        ret = "\t"*level + str(self.letter) + "\n" + \
            "\t"*level + self.mbr.__repr__(level) + "\n"
        return ret
