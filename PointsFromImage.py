import random
from typing import List

import numpy as np
import skimage
import matplotlib.pyplot as plt
from Lines import Point2D


def pointsFromImage(gray_img: np.ndarray, n_points: int) -> List[Point2D]:
    # blur
    downscale_factor = 2
    pick_padding = 0
    sigma = 1.5
    img = skimage.filters.gaussian(gray_img, sigma=sigma)
    downscaled_image = img[::downscale_factor, ::downscale_factor]
    img = downscaled_image
    img = skimage.filters.sobel(img)
    img = img ** 1.25

    plt.imshow(img)
    plt.show()

    # Randomly select points.
    h, w = downscaled_image.shape
    assert w * h >= n_points

    points = []

    while len(points) < n_points:
        r = random.randint(0, h - 1)
        c = random.randint(0, w - 1)
        p = random.uniform(0, 1)

        if img[r-pick_padding:r+pick_padding+1, c-pick_padding:c+pick_padding+1].sum() / (2*pick_padding+1)**2 >= p:
            points.append(Point2D(c * downscale_factor, (h - r - 1) * downscale_factor))
            img[r - pick_padding:r + pick_padding + 1, c - pick_padding:c + pick_padding + 1] = 0.0

    return points


