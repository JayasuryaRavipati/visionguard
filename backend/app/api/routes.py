import json
import time
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.cv.features import decode_image
from app.services.analyzer import analyze_image
from app.database.database import get_db
from app.database.models import AnalysisRecord


router = APIRouter(
    prefix="/api",
    tags=["Image Analysis"],
)


# ============================================================
# CONFIGURATION
# ============================================================

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE = 10 * 1024 * 1024


# backend/
BASE_DIR = Path(
    __file__
).resolve().parents[2]


# backend/uploads/
UPLOAD_DIR = (
    BASE_DIR / "uploads"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# CONTENT TYPE -> EXTENSION
# ============================================================

CONTENT_TYPE_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


# ============================================================
# SAFE JSON LOADER
# ============================================================

def safe_json_loads(
    value,
    default,
):
    """
    Safely convert JSON stored as text
    back into a Python object.
    """

    if not value:
        return default

    try:
        return json.loads(value)

    except (
        json.JSONDecodeError,
        TypeError,
    ):
        return default


# ============================================================
# ANALYZE IMAGE
# ============================================================

@router.post("/analyze")
async def analyze_uploaded_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Validate file type
    # --------------------------------------------------------

    if (
        file.content_type
        not in ALLOWED_CONTENT_TYPES
    ):
        raise HTTPException(
            status_code=415,
            detail=(
                "Unsupported file type. "
                "Please upload JPEG, PNG, "
                "or WEBP."
            ),
        )

    # --------------------------------------------------------
    # Read uploaded file
    # --------------------------------------------------------

    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Uploaded file is empty."
            ),
        )

    if (
        len(file_bytes)
        > MAX_FILE_SIZE
    ):
        raise HTTPException(
            status_code=413,
            detail=(
                "Image exceeds the maximum "
                "allowed size of 10 MB."
            ),
        )

    # --------------------------------------------------------
    # Decode image
    # --------------------------------------------------------

    image = decode_image(
        file_bytes
    )

    if image is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "The uploaded image "
                "could not be read or "
                "appears corrupted."
            ),
        )

    # --------------------------------------------------------
    # Analyze image + measure processing time
    # --------------------------------------------------------

    try:
        start_time = (
            time.perf_counter()
        )

        analysis = analyze_image(
            image
        )

        processing_ms = round(
            (
                time.perf_counter()
                - start_time
            )
            * 1000
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Image analysis failed."
            ),
        ) from exc

    # --------------------------------------------------------
    # Generate unique saved image name
    # --------------------------------------------------------

    extension = (
        CONTENT_TYPE_EXTENSIONS[
            file.content_type
        ]
    )

    saved_filename = (
        f"{uuid4().hex}"
        f"{extension}"
    )

    saved_image_path = (
        UPLOAD_DIR
        / saved_filename
    )

    # --------------------------------------------------------
    # Save actual image
    # --------------------------------------------------------

    try:
        saved_image_path.write_bytes(
            file_bytes
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Image was analyzed but "
                "could not be saved."
            ),
        ) from exc

    # --------------------------------------------------------
    # Database image path
    # --------------------------------------------------------

    image_path = (
        f"/uploads/"
        f"{saved_filename}"
    )

    # --------------------------------------------------------
    # Save analysis to SQLite
    # --------------------------------------------------------

    record = AnalysisRecord(
        filename=(
            file.filename
            or saved_filename
        ),

        content_type=(
            file.content_type
        ),

        image_path=(
            image_path
        ),

        # Actual uploaded file size
        # in bytes.
        file_size=(
            len(file_bytes)
        ),

        quality_score=(
            analysis[
                "quality_score"
            ]
        ),

        quality_label=(
            analysis[
                "quality_label"
            ]
        ),

        confidence=(
            analysis.get(
                "confidence"
            )
        ),

        score_uncertainty=(
            analysis.get(
                "score_uncertainty"
            )
        ),

        # Actual time taken for
        # analysis in milliseconds.
        processing_ms=(
            processing_ms
        ),

        issues_json=json.dumps(
            analysis.get(
                "issues",
                {},
            )
        ),

        statistics_json=json.dumps(
            analysis.get(
                "image_statistics",
                {},
            )
        ),

        ml_prediction_json=json.dumps(
            analysis.get(
                "ml_prediction",
                {},
            )
        ),
    )

    # --------------------------------------------------------
    # Commit database record
    # --------------------------------------------------------

    try:
        db.add(record)
        db.commit()
        db.refresh(record)

    except Exception as exc:
        db.rollback()

        # Remove image if database
        # storage failed.
        try:
            if saved_image_path.exists():
                saved_image_path.unlink()

        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail=(
                "Analysis completed but "
                "could not be saved."
            ),
        ) from exc

    # --------------------------------------------------------
    # Image statistics
    # --------------------------------------------------------

    statistics = analysis.get(
        "image_statistics",
        {},
    )

    # --------------------------------------------------------
    # API response
    # --------------------------------------------------------

    return {
        "id": (
            record.id
        ),

        "filename": (
            record.filename
        ),

        "content_type": (
            record.content_type
        ),

        # IMPORTANT:
        # Use API endpoint rather than
        # direct /uploads path.
        "image_url": (
            f"/api/history/"
            f"{record.id}/image"
        ),

        "quality_score": (
            record.quality_score
        ),

        "quality_label": (
            record.quality_label
        ),

        "confidence": (
            record.confidence
        ),

        "score_uncertainty": (
            record.score_uncertainty
        ),

        "processing_ms": (
            record.processing_ms
        ),

        "image": {
            "filename": (
                record.filename
            ),

            "content_type": (
                record.content_type
            ),

            "size_bytes": (
                record.file_size
            ),

            "width": (
                statistics.get(
                    "width"
                )
            ),

            "height": (
                statistics.get(
                    "height"
                )
            ),

            "format": (
                record.content_type
                .replace(
                    "image/",
                    "",
                )
                .upper()
                if record.content_type
                else None
            ),
        },

        "analysis": (
            analysis
        ),
    }


# ============================================================
# GET STORED ANALYSIS IMAGE
# ============================================================

@router.get(
    "/history/{analysis_id}/image"
)
def get_analysis_image(
    analysis_id: int,
    db: Session = Depends(get_db),
):
    """
    Returns the original image associated
    with an analysis history record.
    """

    record = (
        db.query(
            AnalysisRecord
        )
        .filter(
            AnalysisRecord.id
            == analysis_id
        )
        .first()
    )

    # --------------------------------------------------------
    # Check database record
    # --------------------------------------------------------

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Analysis record "
                "not found."
            ),
        )

    # --------------------------------------------------------
    # Check image path
    # --------------------------------------------------------

    if not record.image_path:
        raise HTTPException(
            status_code=404,
            detail=(
                "Image is not "
                "available for this "
                "analysis."
            ),
        )

    # --------------------------------------------------------
    # Extract filename safely
    # --------------------------------------------------------

    stored_filename = Path(
        record.image_path
    ).name

    image_file = (
        UPLOAD_DIR
        / stored_filename
    )

    # --------------------------------------------------------
    # Check actual image exists
    # --------------------------------------------------------

    if not image_file.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "Stored image file "
                "was not found."
            ),
        )

    # --------------------------------------------------------
    # Return image
    # --------------------------------------------------------

    return FileResponse(
        path=str(
            image_file
        ),

        media_type=(
            record.content_type
            or
            "application/octet-stream"
        ),
    )


# ============================================================
# GET SINGLE ANALYSIS DETAILS
# ============================================================

@router.get(
    "/history/{analysis_id}"
)
def get_analysis_details(
    analysis_id: int,
    db: Session = Depends(get_db),
):
    """
    Returns complete information for
    one analysis history record.
    """

    record = (
        db.query(
            AnalysisRecord
        )
        .filter(
            AnalysisRecord.id
            == analysis_id
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Analysis record "
                "not found."
            ),
        )

    # --------------------------------------------------------
    # Decode stored JSON
    # --------------------------------------------------------

    statistics = safe_json_loads(
        record.statistics_json,
        {},
    )

    issues = safe_json_loads(
        record.issues_json,
        {},
    )

    ml_prediction = safe_json_loads(
        record.ml_prediction_json,
        {},
    )

    # --------------------------------------------------------
    # Complete response
    # --------------------------------------------------------

    return {
        "id": (
            record.id
        ),

        "filename": (
            record.filename
        ),

        "content_type": (
            record.content_type
        ),

        "image_url": (
            f"/api/history/"
            f"{record.id}/image"
        ),

        "quality_score": (
            record.quality_score
        ),

        "quality_label": (
            record.quality_label
        ),

        "confidence": (
            record.confidence
        ),

        "score_uncertainty": (
            record.score_uncertainty
        ),

        "processing_ms": (
            record.processing_ms
        ),

        "issues": (
            issues
        ),

        "image_statistics": (
            statistics
        ),

        "image": {
            "filename": (
                record.filename
            ),

            "content_type": (
                record.content_type
            ),

            "size_bytes": (
                record.file_size
            ),

            "width": (
                statistics.get(
                    "width"
                )
            ),

            "height": (
                statistics.get(
                    "height"
                )
            ),

            "format": (
                record.content_type
                .replace(
                    "image/",
                    "",
                )
                .upper()
                if record.content_type
                else None
            ),
        },

        "ml_prediction": (
            ml_prediction
        ),

        "created_at": (
            record.created_at.isoformat()
            if record.created_at
            else None
        ),
    }


# ============================================================
# ANALYSIS HISTORY
# ============================================================

@router.get("/history")
def get_analysis_history(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """
    Returns recent image analyses.
    """

    # --------------------------------------------------------
    # Prevent extremely large responses
    # --------------------------------------------------------

    limit = max(
        1,
        min(
            limit,
            100,
        ),
    )

    # --------------------------------------------------------
    # Read database records
    # --------------------------------------------------------

    records = (
        db.query(
            AnalysisRecord
        )
        .order_by(
            AnalysisRecord
            .created_at
            .desc()
        )
        .limit(limit)
        .all()
    )

    history = []

    # --------------------------------------------------------
    # Build response
    # --------------------------------------------------------

    for record in records:
        statistics = safe_json_loads(
            record.statistics_json,
            {},
        )

        issues = safe_json_loads(
            record.issues_json,
            {},
        )

        ml_prediction = safe_json_loads(
            record.ml_prediction_json,
            {},
        )

        history.append(
            {
                "id": (
                    record.id
                ),

                "filename": (
                    record.filename
                ),

                "content_type": (
                    record.content_type
                ),

                # This URL now works
                # through the API.
                "image_url": (
                    f"/api/history/"
                    f"{record.id}/image"
                ),

                "quality_score": (
                    record.quality_score
                ),

                "quality_label": (
                    record.quality_label
                ),

                "confidence": (
                    record.confidence
                ),

                "score_uncertainty": (
                    record
                    .score_uncertainty
                ),

                "processing_ms": (
                    record.processing_ms
                ),

                "issues": (
                    issues
                ),

                "image_statistics": (
                    statistics
                ),

                # Convenient image metadata
                # for the frontend modal.
                "image": {
                    "filename": (
                        record.filename
                    ),

                    "content_type": (
                        record.content_type
                    ),

                    "size_bytes": (
                        record.file_size
                    ),

                    "width": (
                        statistics.get(
                            "width"
                        )
                    ),

                    "height": (
                        statistics.get(
                            "height"
                        )
                    ),

                    "format": (
                        record.content_type
                        .replace(
                            "image/",
                            "",
                        )
                        .upper()
                        if record.content_type
                        else None
                    ),
                },

                "ml_prediction": (
                    ml_prediction
                ),

                "created_at": (
                    record
                    .created_at
                    .isoformat()
                    if record.created_at
                    else None
                ),
            }
        )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "count": len(
            history
        ),

        "results": (
            history
        ),
    }