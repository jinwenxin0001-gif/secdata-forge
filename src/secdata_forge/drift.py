from __future__ import annotations

import math
from typing import Any

from .utils import parse_float


def detect_drift(
    reference: list[dict[str, Any]],
    current: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    numeric_features = config.get("numeric_features") or infer_numeric_features(reference, current)
    categorical_features = config.get("categorical_features") or ["label"]
    numeric_results = []
    categorical_results = []

    for feature in numeric_features:
        left = [value for value in (parse_float(row.get(feature)) for row in reference) if value is not None]
        right = [value for value in (parse_float(row.get(feature)) for row in current) if value is not None]
        if left and right:
            psi = population_stability_index(left, right)
            ks = ks_statistic(left, right)
            numeric_results.append(
                {
                    "feature": feature,
                    "psi": round(psi, 4),
                    "ks": round(ks, 4),
                    "severity": numeric_severity(psi, ks),
                }
            )

    for feature in categorical_features:
        left_dist = distribution(row.get(feature) for row in reference)
        right_dist = distribution(row.get(feature) for row in current)
        if left_dist and right_dist:
            js = js_divergence(left_dist, right_dist)
            categorical_results.append(
                {
                    "feature": feature,
                    "js_divergence": round(js, 4),
                    "severity": categorical_severity(js),
                    "reference_distribution": left_dist,
                    "current_distribution": right_dist,
                }
            )

    high = sum(1 for item in numeric_results + categorical_results if item["severity"] == "high")
    medium = sum(1 for item in numeric_results + categorical_results if item["severity"] == "medium")
    return {
        "numeric_drift": numeric_results,
        "categorical_drift": categorical_results,
        "summary": {
            "features_checked": len(numeric_results) + len(categorical_results),
            "high_drift_features": high,
            "medium_drift_features": medium,
            "overall_status": "update_required" if high else "watch" if medium else "stable",
        },
    }


def infer_numeric_features(*tables: list[dict[str, Any]]) -> list[str]:
    candidates: set[str] = set()
    for table in tables:
        for record in table[:50]:
            for key, value in record.items():
                if key.startswith("_"):
                    continue
                if parse_float(value) is not None:
                    candidates.add(key)
    return sorted(candidates)


def population_stability_index(reference: list[float], current: list[float], bins: int = 10) -> float:
    low = min(reference)
    high = max(reference)
    if low == high:
        return 0.0 if min(current) == max(current) == low else 1.0
    width = (high - low) / bins
    ref_counts = [0] * bins
    cur_counts = [0] * bins
    for value in reference:
        ref_counts[min(bins - 1, max(0, int((value - low) / width)))] += 1
    for value in current:
        cur_counts[min(bins - 1, max(0, int((value - low) / width)))] += 1
    psi = 0.0
    for ref_count, cur_count in zip(ref_counts, cur_counts):
        ref_ratio = max(ref_count / len(reference), 1e-6)
        cur_ratio = max(cur_count / len(current), 1e-6)
        psi += (cur_ratio - ref_ratio) * math.log(cur_ratio / ref_ratio)
    return psi


def ks_statistic(reference: list[float], current: list[float]) -> float:
    values = sorted(set(reference + current))
    ref_sorted = sorted(reference)
    cur_sorted = sorted(current)
    ref_index = 0
    cur_index = 0
    max_gap = 0.0
    for value in values:
        while ref_index < len(ref_sorted) and ref_sorted[ref_index] <= value:
            ref_index += 1
        while cur_index < len(cur_sorted) and cur_sorted[cur_index] <= value:
            cur_index += 1
        max_gap = max(max_gap, abs(ref_index / len(ref_sorted) - cur_index / len(cur_sorted)))
    return max_gap


def distribution(values: Any) -> dict[str, float]:
    counts: dict[str, int] = {}
    total = 0
    for value in values:
        key = str(value or "missing")
        counts[key] = counts.get(key, 0) + 1
        total += 1
    return {key: round(count / total, 6) for key, count in counts.items()} if total else {}


def js_divergence(left: dict[str, float], right: dict[str, float]) -> float:
    keys = set(left) | set(right)
    left_values = [left.get(key, 0.0) for key in keys]
    right_values = [right.get(key, 0.0) for key in keys]
    midpoint = [(a + b) / 2 for a, b in zip(left_values, right_values)]
    return 0.5 * kl_divergence(left_values, midpoint) + 0.5 * kl_divergence(right_values, midpoint)


def kl_divergence(left: list[float], right: list[float]) -> float:
    total = 0.0
    for a, b in zip(left, right):
        a = max(a, 1e-9)
        b = max(b, 1e-9)
        total += a * math.log(a / b)
    return total


def numeric_severity(psi: float, ks: float) -> str:
    if psi >= 0.25 or ks >= 0.35:
        return "high"
    if psi >= 0.1 or ks >= 0.2:
        return "medium"
    return "low"


def categorical_severity(js: float) -> str:
    if js >= 0.18:
        return "high"
    if js >= 0.06:
        return "medium"
    return "low"

