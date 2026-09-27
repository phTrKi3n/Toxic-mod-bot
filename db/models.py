"""
db/models.py — ORM khớp đúng ERD đã chốt ở Chương III của báo cáo.
Không tự thêm bảng hoặc trường mới ở đây; mọi thay đổi entity phải đi qua
thống nhất chung (rule.md mục 7) và ghi log trước khi sửa file này.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "app_user"
    __table_args__ = (
        CheckConstraint(
            "role IN ('member','mod','labeler','admin')", name="ck_user_role"
        ),
    )

    user_id: Mapped[int] = mapped_column(primary_key=True)
    discord_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="member")
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Server(Base):
    __tablename__ = "server"

    server_id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    threshold_low: Mapped[float] = mapped_column(Float, default=0.30)
    threshold_high: Mapped[float] = mapped_column(Float, default=0.90)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Message(Base):
    __tablename__ = "message"

    message_id: Mapped[int] = mapped_column(primary_key=True)
    server_id: Mapped[int] = mapped_column(
        ForeignKey("server.server_id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("app_user.user_id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ModelVersion(Base):
    __tablename__ = "model_version"

    model_version_id: Mapped[int] = mapped_column(primary_key=True)
    version_tag: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    trained_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    training_set_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    f1_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)


class Classification(Base):
    __tablename__ = "classification"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 1", name="ck_score_range"),
    )

    classification_id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(
        ForeignKey("message.message_id"), nullable=False
    )
    model_version_id: Mapped[int] = mapped_column(
        ForeignKey("model_version.model_version_id"), nullable=False
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ModerationAction(Base):
    __tablename__ = "moderation_action"
    __table_args__ = (
        CheckConstraint(
            "action_type IN ('ignore','flag','delete','restore')", name="ck_action_type"
        ),
    )

    action_id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(
        ForeignKey("message.message_id"), nullable=False
    )
    action_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # decided_by = NULL nghĩa là bot tự quyết định (không có mod can thiệp)
    decided_by: Mapped[int | None] = mapped_column(
        ForeignKey("app_user.user_id"), nullable=True
    )
    decided_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Appeal(Base):
    __tablename__ = "appeal"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','approved','rejected')", name="ck_appeal_status"
        ),
        UniqueConstraint("message_id", name="uq_appeal_message"),
    )

    appeal_id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(
        ForeignKey("message.message_id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("app_user.user_id"), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    resolved_by: Mapped[int | None] = mapped_column(
        ForeignKey("app_user.user_id"), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class HardCase(Base):
    __tablename__ = "hard_case"
    __table_args__ = (
        CheckConstraint(
            "corrected_label IN ('toxic','not_toxic') OR corrected_label IS NULL",
            name="ck_hardcase_label",
        ),
        CheckConstraint(
            "status IN ('pending','labeled','used_in_training')",
            name="ck_hardcase_status",
        ),
    )

    hardcase_id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(
        ForeignKey("message.message_id"), nullable=False
    )
    original_score: Mapped[float] = mapped_column(Float, nullable=False)
    corrected_label: Mapped[str | None] = mapped_column(String(20), nullable=True)
    labeled_by: Mapped[int | None] = mapped_column(
        ForeignKey("app_user.user_id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default="pending")
