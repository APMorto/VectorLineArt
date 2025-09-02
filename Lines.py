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


class Board(object):
    def __init__(self, lines=None, points=None, bounds=None, seed=None):
        if bounds is None:
            bounds = Bounds(0, 0, 0, 0)
        if lines is None:
            lines = []
        if points is None:
            points = []
        self.lines = lines
        self.points = points
        self.bounds = bounds

        self.tried = set()

        self.dragging = False

    def lineIntersectsAny(self, line: Line):
        # If it shares a vertex, it does not intersect. Don't forget duplicates though.
        if line in self.lines: return True
        return any(not Line.sharesVertex(l, line) and Line.collides(l, line, 1e-6) for l in self.lines)

    @staticmethod
    def randomPoints(bounds: Bounds, n: int):
        points = bounds.randomPoints(n)
        numPoints = len(points)
        numUniquePoints = len(set(points))
        print(f"Points: {numPoints}, Unique Points: {numUniquePoints}")
        return Board([], points, bounds)

    def draw(self):
        self.draw_lines(self.lines, self.points, self.bounds)

    def randomPointIdx(self):
        return random.randrange(0, len(self.points))

    def distancesToPoint(self, p):
        return [Point2D.distance(p, self.points[i]) for i in range(len(self.points))]

    def pointConnectionProbabilities(self, idx: int):
        p = self.points[idx]
        distances = self.distancesToPoint(p)

        scores = [(i, 1.0 / (d**2)) for i, d in enumerate(distances) if i != idx]
        return scores

    def randomNonCollidingConnection(self):
        while len(self.tried) < len(self.points):
            idx = self.randomPointIdx()
            if idx in self.tried: continue
            #self.tried.add(idx)
            p = self.points[idx]

            idxsAndProbs = self.pointConnectionProbabilities(idx)
            failed = 0
            weights = [w for i, w in idxsAndProbs]
            while failed < len(idxsAndProbs):
                candidate = random.choices(range(len(weights)), weights=weights, k=1)[0]
                chosenPoint = self.points[idxsAndProbs[candidate][0]]


                linesCandidate = Line(p, chosenPoint)
                if not self.lineIntersectsAny(linesCandidate):
                    return linesCandidate
                else:
                    failed += 1
                    weights[candidate] = 0.0
            self.tried.add(idx)

    def addWeightedConnection(self):
        line = self.randomNonCollidingConnection()
        if line is not None:
            self.lines.append(line)
            return True
        else:
            return False

    def draw_lines(self, lines, points, bounds=None):
        """
        Draws white lines on a black background using matplotlib.
        The figure is interactive (zoom, pan, save).

        Parameters
        ----------
        lines : iterable
            Iterable of objects with attributes: p1.x, p1.y, p2.x, p2.y.
        """
        fig, ax = plt.subplots(dpi=300)
        fig.patch.set_facecolor('black')
        ax.set_facecolor("black")

        def make():
            for line in lines:
                x_values = [line.p1.x, line.p2.x]
                y_values = [line.p1.y, line.p2.y]
                ax.plot(x_values, y_values, color="white", linewidth=0.5)

            for point in points:
                ax.scatter(point.x, point.y, color="white", s=0.5)

            if bounds is None:
                ax.autoscale_view()
                ax.set_aspect("equal", adjustable="datalim")
            else:
                pad = 1
                ax.set_xlim(bounds.left - pad, bounds.right + pad)
                ax.set_ylim(bounds.bottom - pad, bounds.top + pad)
            ax.axis("off")

        make()

        # --- Event handler ---
        def on_click(event):
            if event.inaxes == ax:
                print(f"Clicked at data coords: ({event.xdata:.3f}, {event.ydata:.3f})")
                self.dragging = True
                self.drawStart = Point2D(event.xdata, event.ydata)

                # Experimental, draws point where clicked.
                ax.scatter(event.xdata, event.ydata, color="white", s=0.5)
                plt.show()

        def on_release(event):
            if self.dragging and event.inaxes == ax:
                print("Released")
                self.drawEnd = Point2D(event.xdata, event.ydata)

                cutLine = Line(self.drawStart, self.drawEnd)
                #self.lines = self.lines + [cutLine]
                self.lines = [line for line in self.lines if not Line.collides(cutLine, line)]
                #fig.clear()
                #make()
                #plt.show()
                plt.close(fig)
                self.draw()
                self.dragging = False



        def on_key(event):
            """Handle key press events."""
            if event.key in ("enter", "return"):
                print("[LineViewer] Enter pressed -> closing window")
                plt.close(fig)

        # Connect the handler
        fig.canvas.mpl_connect("button_press_event", on_click)
        fig.canvas.mpl_connect("key_press_event", on_key)
        fig.canvas.mpl_connect("button_release_event", on_release)

        plt.show()


board = Board.randomPoints(Bounds(-50, 50, -50, 50), 100)
for i in range(1000):
    if not board.addWeightedConnection():
       break
    #if i % 50 == 0:
    #    board.draw()
board.draw()

sl = sorted(board.lines)
print(sl)
exit(0)
