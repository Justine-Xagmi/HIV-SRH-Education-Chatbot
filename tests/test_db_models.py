
from app.db.base import Base
from app.db import models  # noqa: F401


EXPECTED_TABLES = {
    "health_sources",
    "knowledge_documents",
    "document_versions",
    "clinical_review_records",
    "knowledge_audit_events",
}


def test_all_governance_tables_are_registered():
    actual_tables = set(Base.metadata.tables.keys())

    assert EXPECTED_TABLES.issubset(actual_tables)


def test_knowledge_document_references_health_source():
    foreign_keys = {
        fk.target_fullname
        for fk in Base.metadata.tables["knowledge_documents"].foreign_keys
    }

    assert "health_sources.id" in foreign_keys


def test_document_version_references_knowledge_document():
    foreign_keys = {
        fk.target_fullname
        for fk in Base.metadata.tables["document_versions"].foreign_keys
    }

    assert "knowledge_documents.id" in foreign_keys


def test_clinical_review_references_document_version():
    foreign_keys = {
        fk.target_fullname
        for fk in Base.metadata.tables["clinical_review_records"].foreign_keys
    }

    assert "document_versions.id" in foreign_keys


def test_document_version_numbers_are_unique_per_document():
    constraints = {
        constraint.name
        for constraint in Base.metadata.tables[
            "document_versions"
        ].constraints
    }

    assert "uq_document_versions_document_version" in constraints
