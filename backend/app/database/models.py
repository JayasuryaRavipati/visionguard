from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)

from app.database.database import Base


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(
        String,
        nullable=False
    )

    content_type = Column(
        String,
        nullable=True
    )

    quality_score = Column(
        Float,
        nullable=False
    )

    quality_label = Column(
        String,
        nullable=False
    )

    confidence = Column(
        Float,
        nullable=False
    )

    issues_json = Column(
        Text,
        nullable=False
    )

    statistics_json = Column(
        Text,
        nullable=False
    )

    ml_prediction_json = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )