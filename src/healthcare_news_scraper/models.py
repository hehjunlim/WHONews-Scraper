from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthcareArticle:
    title: str
    date: str
    category: str
    url: str
    source: str
