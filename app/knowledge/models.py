
from datetime import date, datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


ReviewStatus = Literal["pending_review", "approved", "retired"]
PermissionStatus = Literal["unknown", "permitted", "restricted"]
IngestionStatus = Literal["pending_validation", "validated", "rejected"]

KnowledgeTopic = Literal[
    "hiv_prevention",
    "hiv_testing",
    "hiv_treatment_education",
    "stigma_discrimination",
    "sexual_health",
    "contraception_family_planning",
    "pregnancy_reproductive_health",
    "sexually_transmitted_infections",
    "other_srh",
]


class HealthSource(BaseModel):
    """Validated metadata describing a knowledge source."""

    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=300)
    organization: str = Field(min_length=1, max_length=200)
    url: HttpUrl
    language: Literal["en", "sw"]
    review_status: ReviewStatus = "pending_review"
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    version: str = Field(min_length=1, max_length=100)
    publication_date: date | None = None
    last_verified_at: datetime | None = None
    permission_status: PermissionStatus = "unknown"


class KnowledgeDocument(BaseModel):
    """Validated knowledge document used by ingestion and review workflows."""

    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(min_length=1, max_length=100)
    source: HealthSource
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1, max_length=20000)
    language: Literal["en", "sw"]
    topics: list[KnowledgeTopic] = Field(default_factory=list)
    ingestion_status: IngestionStatus = "pending_validation"
    review_status: ReviewStatus = "pending_review"
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
