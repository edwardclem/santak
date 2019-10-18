# computer vision utilities for santak

import numpy as np


def subsample_contours(contours, pct=0.2, min_threshold=10):
    """
    Samples subset of contour points.
    """
    subsampled_contours = []
    for contour in contours:
        total_points = contour.shape[0]
        num_to_sample = (
            int(pct * total_points) if total_points > min_threshold else total_points
        )
        sample_idx = np.sort(
            np.random.choice(total_points, num_to_sample, replace=False)
        )
        subsampled_contours.append(contour[sample_idx, :, :])

    return subsampled_contours


def reduce_contours(contours, step=6):
    """
    keeps every step points, removes the rest. Alternative to probabilistic subsampling.
    TODO: add min threshold? i suspect that the abort trap present in the search function is due to too few points.
    """

    reduced_contours = []
    for contour in contours:
        total_points = contour.shape[0]
        kept_idx = np.arange(0, total_points, step)
        reduced_contours.append(contour[kept_idx, :, :])

    return reduced_contours
