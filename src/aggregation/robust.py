"""Robust aggregation rules applied ACROSS cluster means.

This is where CB-SAFE resolves the hide-versus-inspect tension: individual updates
are hidden inside cluster sums by secure aggregation (the server never sees them),
and robustness operates only on the k visible cluster means. A cluster mean is
contaminated if any member is malicious, so with malicious fraction f and cluster
size c the probability a cluster stays clean is (1-f)**c — the quantitative
privacy-robustness trade-off the experiments sweep.
"""

from __future__ import annotations

import numpy as np


def mean(cluster_means: np.ndarray) -> np.ndarray:
    return cluster_means.mean(axis=0)


def median(cluster_means: np.ndarray) -> np.ndarray:
    return np.median(cluster_means, axis=0)


def trimmed_mean(cluster_means: np.ndarray, trim: int = 2) -> np.ndarray:
    """Coordinate-wise trimmed mean: drop `trim` extremes per side, average the rest."""
    k = cluster_means.shape[0]
    if 2 * trim >= k:
        raise ValueError(f"trim={trim} too large for k={k} clusters")
    s = np.sort(cluster_means, axis=0)
    return s[trim : k - trim].mean(axis=0)


def multi_krum(cluster_means: np.ndarray, n_byzantine: int = 2, n_select: int | None = None) -> np.ndarray:
    """Multi-Krum over cluster means: score by sum of closest k-b-2 squared distances,
    average the n_select lowest-scored vectors."""
    k = cluster_means.shape[0]
    n_select = n_select or max(1, k - 2 * n_byzantine)
    d2 = ((cluster_means[:, None, :] - cluster_means[None, :, :]) ** 2).sum(axis=2)
    n_close = max(1, k - n_byzantine - 2)
    scores = np.array([np.sort(d2[i][np.arange(k) != i])[:n_close].sum() for i in range(k)])
    chosen = np.argsort(scores)[:n_select]
    return cluster_means[chosen].mean(axis=0)


AGGREGATORS = {
    "mean": mean,
    "median": median,
    "trimmed": trimmed_mean,
    "krum": multi_krum,
}
