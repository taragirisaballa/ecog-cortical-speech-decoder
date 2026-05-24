"""Synthetic ECoG-like data for fast decoder smoke tests."""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, filtfilt, hilbert


def make_synthetic_ecog(
    *,
    n_trials: int = 160,
    n_channels: int = 32,
    n_times: int = 400,
    sampling_rate: float = 200.0,
    random_state: int = 7,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Create ECoG-like trials with class-specific high-gamma bursts."""

    rng = np.random.default_rng(random_state)
    labels = np.repeat([0, 1], n_trials // 2)
    rng.shuffle(labels)

    data = rng.normal(0, 0.7, size=(n_trials, n_channels, n_times))
    time = np.arange(n_times) / sampling_rate
    carrier = np.sin(2 * np.pi * 75 * time)
    window = np.exp(-0.5 * ((time - 1.0) / 0.18) ** 2)
    burst = carrier * window

    class_0_channels = slice(3, 9)
    class_1_channels = slice(18, 24)
    for trial_idx, label in enumerate(labels):
        target_channels = class_1_channels if label else class_0_channels
        data[trial_idx, target_channels, :] += 1.4 * burst

    return data, labels, sampling_rate


def high_gamma_power(
    trials: np.ndarray,
    sampling_rate: float,
    band: tuple[float, float] = (70.0, 110.0),
) -> np.ndarray:
    """Estimate trial-by-channel high-gamma power with a Hilbert envelope."""

    nyquist = sampling_rate / 2
    high = min(band[1] / nyquist, 0.99)
    low = band[0] / nyquist
    b, a = butter(4, [low, high], btype="bandpass")
    filtered = filtfilt(b, a, trials, axis=-1)
    envelope = np.abs(hilbert(filtered, axis=-1))
    return np.log1p(envelope.mean(axis=-1))


def run_decoder_smoke_test(random_state: int = 7) -> dict[str, float]:
    """Run a tiny decoding pipeline to prove the analysis stack works."""

    trials, labels, sampling_rate = make_synthetic_ecog(random_state=random_state)
    features = high_gamma_power(trials, sampling_rate)
    predictions = _cross_validated_nearest_centroid(features, labels, random_state=random_state)
    return {"accuracy": float(np.mean(predictions == labels)), "chance": 0.5}


def _cross_validated_nearest_centroid(
    features: np.ndarray,
    labels: np.ndarray,
    *,
    n_splits: int = 5,
    random_state: int = 7,
) -> np.ndarray:
    """Dependency-light classifier for validating features without scikit-learn."""

    rng = np.random.default_rng(random_state)
    predictions = np.empty_like(labels)
    for test_idx in _stratified_folds(labels, n_splits=n_splits, rng=rng):
        train_mask = np.ones(labels.shape[0], dtype=bool)
        train_mask[test_idx] = False
        train_x = features[train_mask]
        train_y = labels[train_mask]

        mean = train_x.mean(axis=0)
        std = train_x.std(axis=0)
        std[std == 0] = 1.0
        train_z = (train_x - mean) / std
        test_z = (features[test_idx] - mean) / std

        classes = np.unique(train_y)
        centroids = np.vstack([train_z[train_y == label].mean(axis=0) for label in classes])
        distances = ((test_z[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
        predictions[test_idx] = classes[np.argmin(distances, axis=1)]
    return predictions


def _stratified_folds(labels: np.ndarray, *, n_splits: int, rng: np.random.Generator) -> list[np.ndarray]:
    folds: list[list[int]] = [[] for _ in range(n_splits)]
    for label in np.unique(labels):
        indices = np.flatnonzero(labels == label)
        rng.shuffle(indices)
        for fold_id, fold_indices in enumerate(np.array_split(indices, n_splits)):
            folds[fold_id].extend(int(index) for index in fold_indices)
    return [np.array(sorted(fold), dtype=int) for fold in folds]
