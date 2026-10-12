from sqlalchemy import (
    Boolean, Column, Float, ForeignKey, Index, Integer, JSON, String, Text,
    TIMESTAMP, text,
)
from sqlalchemy.orm import relationship
from ..db.session import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True)
    channel = Column(String(20), nullable=False, default="rest")
    language = Column(String(5), nullable=False, default="en")
    status = Column(String(20), nullable=False, default="active")
    current_tier = Column(Integer, nullable=False, default=1)
    risk_level = Column(String(20), nullable=True)
    risk_score = Column(Float, nullable=True)
    urgent_referral = Column(Boolean, nullable=False, default=False)
    referral_reasons = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )
    completed_at = Column(TIMESTAMP, nullable=True)

    answers = relationship("Answer", back_populates="session", cascade="all, delete-orphan")
    conversation_turns = relationship("ConversationTurn", back_populates="session", cascade="all, delete-orphan")
    risk_result = relationship("RiskResult", back_populates="session", uselist=False, cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"
    __table_args__ = (
        Index("uq_session_factor", "session_id", "factor_id", unique=True),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    factor_id = Column(String(10), nullable=False)
    value = Column(String(255), nullable=False)
    raw_utterance = Column(Text, nullable=True)
    recorded_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    session = relationship("Session", back_populates="answers")


class ConversationTurn(Base):
    __tablename__ = "conversation_turns"
    __table_args__ = (
        Index("idx_session_turn", "session_id", "turn_number"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    turn_number = Column(Integer, nullable=False)
    role = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True)
    tool_results = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    session = relationship("Session", back_populates="conversation_turns")


class RiskResult(Base):
    __tablename__ = "risk_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    risk_level = Column(String(20), nullable=False)
    risk_probability = Column(Float, nullable=False)
    key_risk_factors = Column(JSON, nullable=False)
    protective_factors = Column(JSON, nullable=False)
    recommendations = Column(JSON, nullable=False)
    model_version = Column(String(20), nullable=False, default="v0.1-mvp")
    computed_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    session = relationship("Session", back_populates="risk_result")
