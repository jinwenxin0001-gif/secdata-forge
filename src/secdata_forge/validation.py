from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any

from .utils import parse_datetime, parse_float


def validate_baseline(records: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    label_field = str(config.get("label_field", "label"))
    features = config.get("numeric_features") or []
    usable = [record for record in records if record.get(label_field)]
    if len(usable) < 6:
        return {"status": "skipped", "reason": "not enough labeled records"}
    features = [feature for feature in features if any(parse_float(record.get(feature)) is not None for record in usable)]
    if not features:
        return {"status": "skipped", "reason": "no numeric features available"}

    train, test = split_records(usable, config)
    if len({record.get(label_field) for record in train}) < 2 or not test:
        return {"status": "skipped", "reason": "train/test split does not contain enough classes"}

    model = fit_centroids(train, features, label_field)
    predictions = [predict_centroid(model, record, features) for record in test]
    truth = [str(record.get(label_field)) for record in test]
    return {
        "status": "ok",
        "model": "nearest-centroid-baseline",
        "features": features,
        "train_records": len(train),
        "test_records": len(test),
        "metrics": metrics(truth, predictions),
        "confusion_matrix": confusion_matrix(truth, predictions),
    }


def split_records(records: list[dict[str, Any]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    timestamp_field = str(config.get("timestamp_field", "timestamp"))
    with_time = [(parse_datetime(record.get(timestamp_field)), record) for record in records]
    if sum(1 for parsed, _ in with_time if parsed is not None) >= len(records) * 0.8:
        ordered = [record for _, record in sorted(with_time, key=lambda item: item[0] or parse_datetime("1970-01-01"))]
    else:
        ordered = list(records)
    cut = max(1, int(len(ordered) * 0.7))
    return ordered[:cut], ordered[cut:]


def fit_centroids(records: list[dict[str, Any]], features: list[str], label_field: str) -> dict[str, Any]:
    means: dict[str, float] = {}
    stds: dict[str, float] = {}
    for feature in features:
        values = [parse_float(record.get(feature)) for record in records]
        numbers = [value for value in values if value is not None]
        means[feature] = sum(numbers) / len(numbers) if numbers else 0.0
        variance = sum((value - means[feature]) ** 2 for value in numbers) / len(numbers) if numbers else 0.0
        stds[feature] = math.sqrt(variance) or 1.0

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record.get(label_field))].append(record)

    centroids: dict[str, dict[str, float]] = {}
    for label, group in grouped.items():
        centroids[label] = {}
        for feature in features:
            values = [parse_float(record.get(feature)) for record in group]
            numbers = [value for value in values if value is not None]
            raw_mean = sum(numbers) / len(numbers) if numbers else means[feature]
            centroids[label][feature] = (raw_mean - means[feature]) / stds[feature]
    return {"centroids": centroids, "means": means, "stds": stds}


def predict_centroid(model: dict[str, Any], record: dict[str, Any], features: list[str]) -> str:
    best_label = ""
    best_distance = float("inf")
    for label, centroid in model["centroids"].items():
        distance = 0.0
        for feature in features:
            value = parse_float(record.get(feature))
            if value is None:
                value = model["means"][feature]
            normalized = (value - model["means"][feature]) / model["stds"][feature]
            distance += (normalized - centroid[feature]) ** 2
        if distance < best_distance:
            best_label = label
            best_distance = distance
    return best_label


def metrics(truth: list[str], predictions: list[str]) -> dict[str, float]:
    labels = sorted(set(truth) | set(predictions))
    correct = sum(1 for expected, actual in zip(truth, predictions) if expected == actual)
    precision_values = []
    recall_values = []
    f1_values = []
    for label in labels:
        tp = sum(1 for expected, actual in zip(truth, predictions) if expected == label and actual == label)
        fp = sum(1 for expected, actual in zip(truth, predictions) if expected != label and actual == label)
        fn = sum(1 for expected, actual in zip(truth, predictions) if expected == label and actual != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        precision_values.append(precision)
        recall_values.append(recall)
        f1_values.append(f1)
    return {
        "accuracy": round(correct / len(truth), 4) if truth else 0.0,
        "macro_precision": round(sum(precision_values) / len(labels), 4) if labels else 0.0,
        "macro_recall": round(sum(recall_values) / len(labels), 4) if labels else 0.0,
        "macro_f1": round(sum(f1_values) / len(labels), 4) if labels else 0.0,
    }


def confusion_matrix(truth: list[str], predictions: list[str]) -> dict[str, dict[str, int]]:
    labels = sorted(set(truth) | set(predictions))
    matrix = {label: {predicted: 0 for predicted in labels} for label in labels}
    for expected, actual in zip(truth, predictions):
        matrix[expected][actual] += 1
    return matrix


def majority_baseline(labels: list[str]) -> str:
    return Counter(labels).most_common(1)[0][0] if labels else ""

