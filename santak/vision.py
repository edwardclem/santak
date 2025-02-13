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


def reduce_contours(contours, step=6, min_points=5):
    """
    keeps every step points, removes the rest. Alternative to probabilistic subsampling.
    """

    reduced_contours = []
    for contour in contours:
        total_points = contour.shape[0]
        kept_idx = np.arange(0, total_points, step)
        if len(kept_idx) > min_points:
            reduced_contours.append(contour[kept_idx, :, :])
        else:
            reduced_contours.append(contour)

    return reduced_contours
