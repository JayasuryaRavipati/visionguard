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
    """
    Stores the result of every image analysis.

    Table:
        analysis_records
    """

    __tablename__ = "analysis_records"

    # ========================================================
    # PRIMARY KEY
    # ========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ========================================================
    # IMAGE INFORMATION
    # ========================================================

    # Original uploaded filename
    # Example: photo.jpg
    filename = Column(
        String,
        nullable=False,
    )

    # MIME type
    # Example: image/jpeg
    content_type = Column(
        String,
        nullable=True,
    )

    # Saved image path
    # Example:
    # /uploads/abc123.jpg
    image_path = Column(
        String,
        nullable=True,
    )

    # Original uploaded file size
    # stored in bytes.
    #
    # Example:
    # 6630 bytes
    file_size = Column(
        Integer,
        nullable=True,
    )

    # ========================================================
    # QUALITY RESULT
    # ========================================================

    # Overall quality score
    # Range: 0 - 100
    quality_score = Column(
        Float,
        nullable=False,
    )

    # ACCEPTABLE
    # DEGRADED
    # DEFECTIVE
    quality_label = Column(
        String,
        nullable=False,
    )

    # ========================================================
    # MACHINE LEARNING INFORMATION
    # ========================================================

    # Actual confidence returned by
    # the trained ML model.
    #
    # Example:
    # 0.824 -> 82.4%
    confidence = Column(
        Float,
        nullable=True,
    )

    # Uncertainty associated with
    # the calculated quality score.
    #
    # Example:
    # 9.7 -> ±9.7
    score_uncertainty = Column(
        Float,
        nullable=True,
    )

    # ========================================================
    # PROCESSING INFORMATION
    # ========================================================

    # Time taken to analyze the image,
    # stored in milliseconds.
    #
    # Example:
    # 245 -> 245 ms
    processing_ms = Column(
        Integer,
        nullable=True,
    )

    # ========================================================
    # JSON ANALYSIS DATA
    # ========================================================

    # Stores detected CV issues.
    #
    # blur
    # underexposure
    # overexposure
    # noise
    # severe_degradation
    # potential_visual_defect
    issues_json = Column(
        Text,
        nullable=False,
    )

    # Stores image statistics:
    #
    # width
    # height
    # sharpness
    # brightness
    # contrast
    # noise
    # intensity_std
    # unique_intensity_values
    statistics_json = Column(
        Text,
        nullable=False,
    )

    # Stores the complete ML result:
    #
    # label
    # confidence
    # probabilities
    ml_prediction_json = Column(
        Text,
        nullable=False,
    )

    # ========================================================
    # TIMESTAMP
    # ========================================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )