from __future__ import annotations

import datetime as dt
import hashlib
import math
from typing import Any, Iterable


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def normalize_key(value: Any) -> str:
    return clean_text(value).lower().replace(" ", "_").replace("-", "_")


def parse_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def parse_datetime(value: Any) -> dt.datetime | None:
    text = clean_text(value)
    if not text:
        return None
    candidates = [
        text,
        text.replace("Z", "+00:00"),
        text.replace("/", "-"),
    ]
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ]
    for candidate in candidates:
        try:
            parsed = dt.datetime.fromisoformat(candidate)
            return parsed.replace(tzinfo=None)
        except ValueError:
            pass
    for fmt in formats:
        try:
            return dt.datetime.strptime(text, fmt)
        except ValueError:
            pass
    return None


def stable_hash(parts: Iterable[Any], length: int = 16) -> str:
    canonical = "|".join(clean_text(part).lower() for part in parts)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:length]


def entropy_score(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    if total <= 0 or len(counts) <= 1:
        return 0.0
    entropy = 0.0
    for count in counts.values():
        if count:
            probability = count / total
            entropy -= probability * math.log(probability)
    return entropy / math.log(len(counts))


def tokens(value: Any) -> set[str]:
    return {token for token in clean_text(value).lower().replace(",", " ").split() if token}


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)

