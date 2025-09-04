import math
import random
from typing import Optional, Union
import matplotlib.pyplot as plt


class Point2D(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other):
        return Point2D(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Point2D(self.x + other.x, self.y + other.y)

    def __str__(self):
        return f"({self.x:.3f},{self.y:.3f})"

    def __truediv__(self, c: float):
        return Point2D(self.x / c, self.y / c)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __iter__(self):
        yield self.x
        yield self.y

    def __lt__(self, other):
        return tuple(self) < tuple(other)

    @staticmethod
    def distance(p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    def norm(self):
        return math.sqrt(self.x**2 + self.y**2)

    def unit(self):
        return self / self.norm()

    def bounds(self):
        return Bounds(self.x, self.x, self.y, self.y)


class Line(object):
    def __init__(self, p1, p2):
        if p1 > p2: # p1 is not right of p2
            p1, p2 = p2, p1
        self.p1 = p1
        self.p2 = p2

    def __iter__(self):
        yield self.p1
        yield self.p2

    def __eq__(self, other):
        return self.p1 == other.p1 and self.p2 == other.p2

    def __lt__(self, other):
        return tuple(self) < tuple(other)

    def dir(self):
        return (self.p2 - self.p1).unit()

    def slope(self):
        dy = (self.p2.y - self.p1.y)
        dx = (self.p2.x - self.p1.x)
        return dy / dx if dx != 0 else math.inf

    def length(self):
        return (self.p1 - self.p2).norm()

    def slopeIntercept(self):
        slope = self.slope()
        intercept = self.p1.y - self.p1.x * slope
        return slope, intercept

    def leftRightBounds(self):
        return self.p1.x, self.p2.x # We assume that they are ordered from construction.

    def bottomTopBounds(self):
        return min(self.p1.y, self.p2.y), max(self.p1.y, self.p2.y)

    def bounds(self):
        return Bounds(*self.leftRightBounds(), *self.bottomTopBounds())

    @staticmethod
    def collides(l1, l2, padding=0.0):
        intercept = Line.intercept(l1, l2)
        if intercept is None:
            return l1 == l2
            # TODO: Properly handle this
            #s1, i1 = l1.slopeIntercept()
            #s2, i2 = l2.slopeIntercept()
            # TODO: handle perfectly vertical
            #if s1 == s2 and i1 == i2:
            #    if s1 == math.inf:
            #        return l1.x == l2.x and
            #if s1 == s2:
            #    if i1 != i2:
        for line in (l1, l2):
            left, right, bottom, top = line.bounds()
            if not (left + padding < intercept.x < right - padding and
                    bottom + padding < intercept.y < top - padding):
                return False
        return True

    @staticmethod
    def intercept(l1, l2) -> Optional[Point2D]:
        xdiff = Point2D(l1.p1.x - l1.p2.x, l2.p1.x - l2.p2.x)
        ydiff = Point2D(l1.p1.y - l1.p2.y, l2.p1.y - l2.p2.y)

        def det(a, b):
            return a.x * b.y - a.y * b.x

        div = det(xdiff, ydiff)
        if div == 0:
            return None

        d = Point2D(det(l1.p1, l1.p2), det(l2.p1, l2.p2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return Point2D(x, y)

    @staticmethod
    def sharesVertex(l1, l2):
        for p1 in l1:
            for p2 in l2:
                if p1 == p2:
                    return True
        return False

    def __str__(self):
        return f"<{self.p1}--{self.p2}>"

    def __repr__(self):
        return str(self)


class Bounds(object):
    def __init__(self, left, right, bottom, top):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        assert left <= right and bottom <= top

    def bounds(self):
        return self

    def expanded(self, other: Union[Point2D, Line, "Bounds"]):
        otherBounds = other.bounds()
        left = min(self.left, otherBounds.left)
        right = max(self.right, otherBounds.right)
        bottom = min(self.bottom, otherBounds.bottom)
        top = max(self.top, otherBounds.top)
        return Bounds(left, right, bottom, top)

    def randomPoint(self):
        return Point2D(random.uniform(self.left, self.right), random.uniform(self.bottom, self.top))

    def randomPoints(self, n: int):
        return [self.randomPoint() for _ in range(n)]

    def __add__(self, other):
        return self.expanded(other)

    def __iter__(self):
        yield self.left
        yield self.right
        yield self.bottom
        yield self.top

    @staticmethod
    def intersects(b1, b2):
        return b1.left <= b2.right and b1.right >= b2.left and b1.bottom <= b2.top and b1.top >= b2.bottom

    def __str__(self):
        return f"<{self.left}--{self.right}--{self.bottom}--{self.top}>"
    __repr__ = __str__

