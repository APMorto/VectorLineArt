import math
from typing import Optional
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
        return f"({self.x}, {self.y})"

    def __truediv__(self, c: float):
        return Point2D(self.x / c, self.y / c)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    @staticmethod
    def distance(p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    def norm(self):
        return math.sqrt(self.x**2 + self.y**2)

    def unit(self):
        return self / self.norm()


class Line(object):
    def __init__(self, p1, p2):
        if p1.x > p2.x: # p1 is not right of p2
            p1, p2 = p2, p1
        self.p1 = p1
        self.p2 = p2

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

    @staticmethod
    def collides(l1, l2):
        intercept = Line.intercept(l1, l2)
        for line in (l1, l2):
            left, right = line.leftRightBounds()
            if not left <= intercept.x <= right:
                return False
            bottom, top = line.bottomTopBounds()
            if not bottom <= intercept.y <= top:
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


def draw_lines(lines, points):
    """
    Draws white lines on a black background using matplotlib.
    The figure is interactive (zoom, pan, save).

    Parameters
    ----------
    lines : iterable
        Iterable of objects with attributes: p1.x, p1.y, p2.x, p2.y.
    """
    fig, ax = plt.subplots()
    fig.patch.set_facecolor('black')
    ax.set_facecolor("black")

    for line in lines:
        x_values = [line.p1.x, line.p2.x]
        y_values = [line.p1.y, line.p2.y]
        ax.plot(x_values, y_values, color="white")

    for point in points:
        ax.scatter(point.x, point.y, color="white")

    ax.autoscale_view()
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")

    # --- Event handler ---
    def on_click(event):
        if event.inaxes == ax:
            print(f"Clicked at data coords: ({event.xdata:.3f}, {event.ydata:.3f})")

    # Connect the handler
    fig.canvas.mpl_connect("button_press_event", on_click)

    plt.show()


origin = Point2D(0, 0)
a = Point2D(10, 20)

down = Point2D(0, -20)
left = Point2D(-14, 1)

l1 = Line(origin, down)
l2 = Line(left, a)

print(Line.intercept(l1, l2))
print(Line.collides(l1, l2))
l3 = Line(origin, Point2D(0, 20))
print(Line.collides(l3, l2))

draw_lines((l1, l2, l3), [Line.intercept(l1, l2)])

