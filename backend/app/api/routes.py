import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.cv.features import decode_image
from app.services.analyzer import analyze_image

from app.database.database import get_db
from app.database.models import AnalysisRecord


router = APIRouter(
    prefix="/api",
    tags=["Image Analysis"]
)


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}

MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/analyze")
async def analyze_uploaded_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # -----------------------------
    # Validate file type
    # -----------------------------

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=(
                "Unsupported file type. "
                "Please upload JPEG, PNG, or WEBP."
            )
        )

    # -----------------------------
    # Read uploaded file
    # -----------------------------

    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=(
                "Image exceeds the maximum "
                "allowed size of 10 MB."
            )
        )

    # -----------------------------
    # Decode image
    # -----------------------------

    image = decode_image(file_bytes)

    if image is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "The uploaded image could not "
                "be read or appears corrupted."
            )
        )

    # -----------------------------
    # Analyze image
    # -----------------------------

    analysis = analyze_image(image)

    # -----------------------------
    # Save analysis to SQLite
    # -----------------------------

    record = AnalysisRecord(
        filename=file.filename,
        content_type=file.content_type,

        quality_score=analysis[
            "quality_score"
        ],

        quality_label=analysis[
            "quality_label"
        ],

        confidence=analysis[
            "confidence"
        ],

        issues_json=json.dumps(
            analysis["issues"]
        ),

        statistics_json=json.dumps(
            analysis["image_statistics"]
        ),

        ml_prediction_json=json.dumps(
            analysis["ml_prediction"]
        ),
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Analysis completed but "
                "could not be saved."
            )
        ) from exc

    # -----------------------------
    # API response
    # -----------------------------

    return {
        "id": record.id,
        "filename": file.filename,
        "content_type": file.content_type,
        "analysis": analysis
    }


@router.get("/history")
def get_analysis_history(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    # Prevent extremely large responses
    limit = max(
        1,
        min(limit, 100)
    )

    records = (
        db.query(AnalysisRecord)
        .order_by(
            AnalysisRecord.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    history = []

    for record in records:
        history.append(
            {
                "id": record.id,
                "filename": record.filename,
                "content_type":
                    record.content_type,

                "quality_score":
                    record.quality_score,

                "quality_label":
                    record.quality_label,

                "confidence":
                    record.confidence,

                "issues":
                    json.loads(
                        record.issues_json
                    ),

                "image_statistics":
                    json.loads(
                        record.statistics_json
                    ),

                "ml_prediction":
                    json.loads(
                        record.ml_prediction_json
                    ),

                "created_at":
                    record.created_at.isoformat()
            }
        )

    return {
        "count": len(history),
        "results": history
    }