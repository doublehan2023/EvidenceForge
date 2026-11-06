import enum
import uuid
from datetime import datetime
from decimal import Decimal

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from evidenceforge_api.db.base import Base


class MembershipRole(str, enum.Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class ResearchRunStatus(str, enum.Enum):
    QUEUED = "queued"
    PLANNING = "planning"
    RETRIEVING = "retrieving"
    EXTRACTING = "extracting"
    RANKING = "ranking"
    SYNTHESIZING = "synthesizing"
    VERIFYING = "verifying"
    PUBLISHED = "published"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"


class SourceStatus(str, enum.Enum):
    DISCOVERED = "discovered"
    FETCHED = "fetched"
    FAILED = "failed"


class ClaimStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    UNSUPPORTED = "unsupported"


class ReportStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    NEEDS_REVIEW = "needs_review"


class ModelCallStatus(str, enum.Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"


def enum_values(enum_class: type[enum.Enum]) -> list[str]:
    """Persist enum values, rather than Python member names, in PostgreSQL."""
    return [str(member.value) for member in enum_class]


class TimestampedModel:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class User(TimestampedModel, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)


class Workspace(TimestampedModel, Base):
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)


class Membership(TimestampedModel, Base):
    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_membership_workspace_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[MembershipRole] = mapped_column(
        Enum(MembershipRole, values_callable=enum_values), nullable=False
    )


class Session(TimestampedModel, Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    refresh_token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, values_callable=enum_values),
        nullable=False,
        default=SessionStatus.ACTIVE,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ResearchRun(TimestampedModel, Base):
    __tablename__ = "research_runs"
    __table_args__ = (Index("ix_research_runs_workspace_status", "workspace_id", "status"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    requested_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ResearchRunStatus] = mapped_column(
        Enum(ResearchRunStatus, values_callable=enum_values),
        nullable=False,
        default=ResearchRunStatus.QUEUED,
    )
    error_message: Mapped[str | None] = mapped_column(Text)


class Source(TimestampedModel, Base):
    __tablename__ = "sources"
    __table_args__ = (Index("ix_sources_run_id", "research_run_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    research_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("research_runs.id", ondelete="CASCADE")
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[SourceStatus] = mapped_column(
        Enum(SourceStatus, values_callable=enum_values),
        nullable=False,
        default=SourceStatus.DISCOVERED,
    )
    storage_key: Mapped[str | None] = mapped_column(String(1024))


class EvidenceChunk(TimestampedModel, Base):
    __tablename__ = "evidence_chunks"
    __table_args__ = (Index("ix_evidence_chunks_source_id", "source_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"))
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))


class Report(TimestampedModel, Base):
    __tablename__ = "reports"
    __table_args__ = (Index("ix_reports_workspace_run", "workspace_id", "research_run_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    research_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("research_runs.id", ondelete="CASCADE"), unique=True
    )
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, values_callable=enum_values), nullable=False, default=ReportStatus.DRAFT
    )
    content: Mapped[str | None] = mapped_column(Text)
    storage_key: Mapped[str | None] = mapped_column(String(1024))


class Claim(TimestampedModel, Base):
    __tablename__ = "claims"
    __table_args__ = (Index("ix_claims_report_id", "report_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    report_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_material: Mapped[bool] = mapped_column(default=True, nullable=False)
    status: Mapped[ClaimStatus] = mapped_column(
        Enum(ClaimStatus, values_callable=enum_values), nullable=False, default=ClaimStatus.PENDING
    )


class Citation(TimestampedModel, Base):
    __tablename__ = "citations"
    __table_args__ = (Index("ix_citations_claim_id", "claim_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    claim_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("claims.id", ondelete="CASCADE"))
    evidence_chunk_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("evidence_chunks.id", ondelete="RESTRICT")
    )
    locator: Mapped[str | None] = mapped_column(String(512))


class Budget(TimestampedModel, Base):
    __tablename__ = "budgets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, unique=True
    )
    monthly_run_limit: Mapped[int | None] = mapped_column(Integer)
    monthly_cost_limit: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))


class ModelCallRecord(TimestampedModel, Base):
    __tablename__ = "model_call_records"
    __table_args__ = (Index("ix_model_calls_run_id", "research_run_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    research_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("research_runs.id", ondelete="CASCADE")
    )
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(200), nullable=False)
    prompt_version: Mapped[str | None] = mapped_column(String(100))
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    cost_usd: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    status: Mapped[ModelCallStatus] = mapped_column(
        Enum(ModelCallStatus, values_callable=enum_values), nullable=False
    )
    error_code: Mapped[str | None] = mapped_column(String(100))
    metadata_json: Mapped[dict[str, object] | None] = mapped_column(JSON)
