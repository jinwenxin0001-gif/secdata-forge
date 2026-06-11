from __future__ import annotations

import datetime as dt
from statistics import median
from typing import Any

from .cleaning import issue_index
from .utils import entropy_score, parse_datetime, parse_float


def score_records(
    records: list[dict[str, Any]],
    issues: list[dict[str, Any]],
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    grouped_issues = issue_index(issues)
    scored: list[dict[str, Any]] = []
    for record in records:
        sample_issues = grouped_issues.get(str(record.get("sample_id")), [])
        dimensions = sample_dimensions(record, sample_issues, config)
        score = weighted_score(dimensions, config.get("quality_weights", {}))
        enriched = dict(record)
        enriched.update({f"_q_{key}": round(value, 4) for key, value in dimensions.items()})
        enriched["_quality_score"] = round(score, 4)
        enriched["_quality_grade"] = grade(score)
        scored.append(enriched)
    return scored, dataset_report(scored, issues, config)


def sample_dimensions(
    record: dict[str, Any],
    issues: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, float]:
    required = [str(field) for field in config.get("required_fields", [])]
    numeric_features = [str(field) for field in config.get("numeric_features", [])]
    label_map = {str(value) for value in config.get("label_mapping", {}).values()}
    label = str(record.get(config.get("label_field", "label"), ""))
    now = dt.datetime.now()

    provenance = parse_float(record.get("_source_trust")) or float(config.get("dataset", {}).get("source_trust", 0.7))
    completeness = completeness_score(record, required)
    label_confidence = 1.0 if label in label_map else 0.35 if label else 0.0
    uniqueness = 1.0
    if any(issue.get("issue") == "near_duplicate" for issue in issues):
        uniqueness = 0.65
    if any(issue.get("issue") == "exact_duplicate" for issue in issues):
        uniqueness = 0.0
    freshness = freshness_score(record.get(config.get("timestamp_field", "timestamp")), now)
    feature = feature_score(record, numeric_features)
    if any(issue.get("issue") == "missing_required" for issue in issues):
        completeness = min(completeness, 0.45)
    if any(issue.get("issue") == "invalid_timestamp" for issue in issues):
        freshness = min(freshness, 0.35)

    return {
        "provenance": clamp(provenance),
        "completeness": completeness,
        "label": clamp(label_confidence),
        "uniqueness": uniqueness,
        "freshness": freshness,
        "feature": feature,
    }


def weighted_score(dimensions: dict[str, float], weights: dict[str, Any]) -> float:
    total_weight = 0.0
    score = 0.0
    for key, value in dimensions.items():
        weight = float(weights.get(key, 1.0))
        total_weight += weight
        score += value * weight
    return clamp(score / total_weight if total_weight else 0.0)


def completeness_score(record: dict[str, Any], required: list[str]) -> float:
    if not required:
        return 1.0
    present = sum(1 for field in required if str(record.get(field, "")).strip())
    return present / len(required)


def freshness_score(value: Any, now: dt.datetime) -> float:
    parsed = parse_datetime(value)
    if parsed is None:
        return 0.5
    age_days = abs((now - parsed).days)
    if age_days <= 180:
        return 1.0
    if age_days >= 3650:
        return 0.2
    return clamp(1.0 - ((age_days - 180) / 3470) * 0.8)


def feature_score(record: dict[str, Any], numeric_features: list[str]) -> float:
    if not numeric_features:
        return 0.8
    usable = sum(1 for field in numeric_features if parse_float(record.get(field)) is not None)
    return usable / len(numeric_features)


def dataset_report(
    records: list[dict[str, Any]],
    issues: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    label_field = str(config.get("label_field", "label"))
    timestamp_field = str(config.get("timestamp_field", "timestamp"))
    threshold = float(config.get("quality_threshold", 0.78))
    labels: dict[str, int] = {}
    sources: dict[str, int] = {}
    ages: list[int] = []
    scores: list[float] = []
    now = dt.datetime.now()
    for record in records:
        labels[str(record.get(label_field) or "missing")] = labels.get(str(record.get(label_field) or "missing"), 0) + 1
        sources[str(record.get("source") or "unknown")] = sources.get(str(record.get("source") or "unknown"), 0) + 1
        score = parse_float(record.get("_quality_score"))
        if score is not None:
            scores.append(score)
        parsed = parse_datetime(record.get(timestamp_field))
        if parsed:
            ages.append(abs((now - parsed).days))

    issue_counts: dict[str, int] = {}
    for issue in issues:
        key = str(issue.get("issue", "unknown"))
        issue_counts[key] = issue_counts.get(key, 0) + 1

    total = len(records)
    high_quality = sum(1 for record in records if float(record.get("_quality_score", 0.0)) >= threshold)
    report = {
        "dataset": config.get("dataset", {}).get("name", "dataset"),
        "records_after_cleaning": total,
        "high_quality_records": high_quality,
        "high_quality_rate": round(high_quality / total, 4) if total else 0.0,
        "overall_quality_score": round(sum(scores) / len(scores), 4) if scores else 0.0,
        "median_age_days": int(median(ages)) if ages else None,
        "label_distribution": labels,
        "source_distribution": sources,
        "balance_score": round(entropy_score(labels), 4),
        "issue_counts": issue_counts,
        "recommendations": recommendations(labels, issue_counts, scores, threshold),
    }
    return report


def recommendations(
    labels: dict[str, int],
    issue_counts: dict[str, int],
    scores: list[float],
    threshold: float,
) -> list[str]:
    advice: list[str] = []
    if labels and entropy_score(labels) < 0.65:
        advice.append("类别分布偏斜，建议构建分层评估集并为少数攻击类型补充样本或设置类别权重。")
    if issue_counts.get("missing_required", 0):
        advice.append("存在关键字段缺失样本，建议完善来源登记和字段映射规则。")
    if issue_counts.get("exact_duplicate", 0) or issue_counts.get("near_duplicate", 0):
        advice.append("检测到重复或近重复样本，建议在版本发布前保留去重清单。")
    if scores and sum(1 for score in scores if score < threshold) / len(scores) > 0.25:
        advice.append("低于质量阈值的样本比例较高，建议进入人工复核或自动修正规则迭代。")
    if not advice:
        advice.append("当前数据质量较稳定，可进入下游模型验证和漂移监测阶段。")
    return advice


def grade(score: float) -> str:
    if score >= 0.9:
        return "A"
    if score >= 0.78:
        return "B"
    if score >= 0.62:
        return "C"
    return "D"


def clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))

