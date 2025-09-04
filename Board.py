import skimage
from matplotlib import pyplot as plt
import random

from Lines import Bounds, Point2D, Line
from PointsFromImage import pointsFromImage


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

    @staticmethod
    def fromImg(path: str, n: int):
        img = skimage.io.imread(path)
        img = skimage.color.rgb2gray(img)
        points = pointsFromImage(img, n)
        return Board([], points, Bounds(0, img.shape[0], 0, img.shape[1]))

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

        def make():
            ax.set_facecolor("black")
            for line in self.lines:
                x_values = [line.p1.x, line.p2.x]
                y_values = [line.p1.y, line.p2.y]
                ax.plot(x_values, y_values, color="white", linewidth=0.5)

            for point in self.points:
                ax.scatter(point.x, point.y, color="white", s=0.5)

            if self.bounds is None:
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
                ax.clear()
                fig.canvas.draw_idle()
                make()
                fig.canvas.draw()
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


#board = Board.randomPoints(Bounds(-50, 50, -50, 50), 100)
img_path = "C:/Users/epicu/OneDrive/Documents/Siemens_onboarding/badge_photo_andrew_morton.jpg"
board = Board.fromImg(img_path, 1500)
for i in range(2000):
    if not board.addWeightedConnection():
       break
    #if i % 50 == 0:
    #    board.draw()
board.draw()

sl = sorted(board.lines)
print(sl)
exit(0)
