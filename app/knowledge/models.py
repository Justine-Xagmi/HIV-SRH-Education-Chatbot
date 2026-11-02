
from datetime import date, datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


ReviewStatus = Literal["pending_review", "approved", "retired"]

PermissionStatus = Literal[
    "unknown",
    "permitted",
    "restricted",
    "prohibited",
]

IngestionStatus = Literal[
    "pending_validation",
    "validated",
    "rejected",
]

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
    permission_basis: str | None = Field(default=None, max_length=2000)
    permission_reference: str | None = Field(default=None, max_length=1000)
    permission_checked_at: datetime | None = None
    permission_checked_by: str | None = Field(default=None, max_length=255)
    permission_notes: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def validate_permission_evidence(self):
        """Validate permission evidence and require it for permitted sources."""

        checked_at = self.permission_checked_at

        if checked_at is not None:
            if checked_at.tzinfo is None or checked_at.utcoffset() is None:
                raise ValueError(
                    "Permission check timestamp must be timezone-aware."
                )

            if checked_at > datetime.now(timezone.utc):
                raise ValueError(
                    "Permission check timestamp cannot be in the future."
                )

        if self.permission_status != "permitted":
            return self

        required_fields = {
            "permission_basis": self.permission_basis,
            "permission_reference": self.permission_reference,
            "permission_checked_at": checked_at,
            "permission_checked_by": self.permission_checked_by,
        }

        missing_fields = [
            field_name
            for field_name, value in required_fields.items()
            if value is None
            or (isinstance(value, str) and not value.strip())
        ]

        if missing_fields:
            raise ValueError(
                "Permission status 'permitted' requires: "
                + ", ".join(missing_fields)
            )

        return self


class KnowledgeDocument(BaseModel):
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
