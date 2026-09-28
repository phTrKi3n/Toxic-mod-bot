import datetime

from sqlalchemy import (
    BIGINT,
    BOOLEAN,
    REAL,
    VARCHAR,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ModelVersion(Base):
    __tablename__ = "model_version"

    model_version_id = Column(Integer, primary_key=True, autoincrement=True)
    version_tag = Column(VARCHAR(50), unique=True, nullable=False)
    trained_at = Column(DateTime, default=datetime.datetime.utcnow)
    training_set_size = Column(Integer, nullable=True)
    f1_score = Column(REAL, nullable=True)
    is_current = Column(BOOLEAN, default=False, nullable=False)

    classifications = relationship("Classification", back_populates="model_version")


class Classification(Base):
    __tablename__ = "classification"

    classification_id = Column(BIGINT, primary_key=True, autoincrement=True)
    message_id = Column(BIGINT, nullable=False)
    model_version_id = Column(
        Integer, ForeignKey("model_version.model_version_id"), nullable=False
    )
    score = Column(REAL, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 1", name="check_score_range"),
    )

    model_version = relationship("ModelVersion", back_populates="classifications")


class ModerationAction(Base):
    __tablename__ = "moderation_action"

    action_id = Column(BIGINT, primary_key=True, autoincrement=True)
    message_id = Column(BIGINT, nullable=False)
    action_type = Column(VARCHAR(20), nullable=False)
    decided_by = Column(Integer, nullable=True)
    decided_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "action_type IN ('ignore', 'flag', 'delete', 'restore')",
            name="check_action_type",
        ),
    )


class Server(Base):
    __tablename__ = "server"

    server_id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(VARCHAR(50), unique=True, nullable=False)
    threshold_low = Column(REAL, default=0.30, nullable=False)
    threshold_high = Column(REAL, default=0.90, nullable=False)
    is_active = Column(BOOLEAN, default=True, nullable=False)


class HardCase(Base):
    __tablename__ = "hard_case"

    hard_case_id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(BIGINT, nullable=False)
    text = Column(VARCHAR(2000), nullable=True)
    score = Column(REAL, nullable=False)
    status = Column(VARCHAR(20), default="pending", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
