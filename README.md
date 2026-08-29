# 🛡️ VisionGuard

## AI-Powered Image Quality & Defect Detection

VisionGuard is a full-stack Computer Vision and Machine Learning application that automatically evaluates the visual quality of uploaded images.

The system detects common image-quality problems such as blur, underexposure, overexposure, image noise, severe degradation, and potential visual defects. It combines traditional computer-vision feature extraction with a trained Machine Learning model to classify the overall image quality.

### Quality Classes

- **ACCEPTABLE** — Image quality is generally good
- **DEGRADED** — Image contains noticeable quality degradation
- **DEFECTIVE** — Image contains significant quality problems

The application also provides an overall quality score, Machine Learning confidence, score uncertainty, image statistics, detected issues, and persistent analysis history.

---

# ✨ Features

## 🔍 Image Quality Detection

VisionGuard analyzes uploaded images for:

- Blur / insufficient sharpness
- Underexposure
- Overexposure
- Image noise
- Severe image degradation
- Potential visual defects

---

## 🤖 AI-Based Quality Classification

A trained **Random Forest Classifier** predicts the overall image quality using computer-vision features extracted from the image.

The Machine Learning model returns:

- Quality label
- Quality score
- Prediction confidence
- Class probabilities
- Score uncertainty

Example:

```text
Quality Score:      76.89 / 100
Quality Label:      ACCEPTABLE
ML Confidence:      52.1%
Score Uncertainty:  ±26.59
```

---

## 📊 Explainable Image Statistics

The application displays interpretable image statistics including:

- Width
- Height
- Sharpness
- Brightness
- Contrast
- Noise
- Intensity standard deviation
- Unique intensity values

The detailed inspection report also displays:

- Image dimensions
- Image format
- File size
- Processing time
- ML model information

---

## 🕘 Analysis History

Completed analyses are stored in a SQLite database.

The Analysis History dashboard displays:

- Filename
- Quality score
- Quality status
- ML confidence
- Score uncertainty
- Detected issues
- Analysis timestamp

Clicking a history record opens a detailed inspection report containing the original image and its complete analysis information.

---

# 🏗️ System Architecture

VisionGuard uses a hybrid **Computer Vision + Machine Learning** architecture.

```text
                    ┌─────────────────┐
                    │      User       │
                    └────────┬────────┘
                             │
                             │ Upload Image
                             ▼
                    ┌─────────────────┐
                    │ React Frontend  │
                    │      Vite       │
                    └────────┬────────┘
                             │
                             │ HTTP / REST
                             ▼
                    ┌─────────────────┐
                    │ FastAPI Backend │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Image Validation│
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │     OpenCV      │
                    │ Feature Extract │
                    └────────┬────────┘
                             │
               ┌─────────────┴─────────────┐
               │                           │
               ▼                           ▼
      ┌─────────────────┐        ┌─────────────────┐
      │ CV Issue        │        │ Random Forest   │
      │ Detection       │        │ ML Classifier   │
      └────────┬────────┘        └────────┬────────┘
               │                           │
               └─────────────┬─────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Quality Result  │
                    └────────┬────────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
                  ▼                     ▼
          ┌──────────────┐      ┌──────────────┐
          │   SQLite     │      │   React UI   │
          │ Persistence  │      │ Visualization│
          └──────────────┘      └──────────────┘
```

---

# 🧠 Machine Learning

## Model

VisionGuard uses a:

```text
RandomForestClassifier
```

for overall image-quality classification.

The model predicts one of three classes:

```text
ACCEPTABLE
DEGRADED
DEFECTIVE
```

The classifier also generates a probability for each class.

Example:

```json
{
  "ACCEPTABLE": 0.5212,
  "DEGRADED": 0.3798,
  "DEFECTIVE": 0.0989
}
```

The class with the highest probability becomes the predicted quality label.

---

# 🧮 ML Features

The Machine Learning model uses **9 engineered features** extracted from the image:

1. Width
2. Height
3. Aspect Ratio
4. Sharpness
5. Brightness
6. Contrast
7. Noise
8. Intensity Standard Deviation
9. Unique Intensity Values

These features are extracted before being passed to the Random Forest classifier.

---

# 📚 Model Training

The model was trained using clean images together with synthetically degraded image samples.

The training process introduces image-quality degradations so the classifier can learn the differences between acceptable, degraded, and defective images.

The dataset was divided using a source-level split to reduce leakage between related clean and degraded samples.

Dataset split used during model development:

```text
Training samples: 1040
Testing samples:   260
```

---

# 📈 Model Performance

The trained Random Forest model achieved:

| Metric | Score |
|---|---:|
| Accuracy | 72.31% |
| Precision | 71.93% |
| Recall | 72.31% |
| F1 Score | 71.92% |

These metrics are based on the held-out test dataset used during model development.

> The model is designed as a practical image-quality classification component for this technical assessment. Performance may vary on image domains that differ significantly from the training data.

---

# 🔄 Image Analysis Pipeline

When an image is uploaded, VisionGuard follows this pipeline:

```text
Upload Image
      │
      ▼
Validate File Type & Size
      │
      ▼
Decode Image
      │
      ▼
Extract Computer Vision Features
      │
      ▼
Detect Individual Quality Issues
      │
      ▼
Build ML Feature Vector
      │
      ▼
Random Forest Prediction
      │
      ▼
Generate Class Probabilities
      │
      ▼
Calculate Quality Score
      │
      ▼
Calculate ML Confidence
      │
      ▼
Calculate Score Uncertainty
      │
      ▼
Store Analysis in SQLite
      │
      ▼
Return Results to React Frontend
```

---

# 🖼️ Computer Vision Analysis

## Blur Detection

VisionGuard analyzes image sharpness to identify images that may be blurred or insufficiently focused.

Possible causes include:

- Motion blur
- Out-of-focus capture
- Loss of fine image details

---

## Underexposure Detection

Image brightness characteristics are analyzed to detect images that are excessively dark.

---

## Overexposure Detection

Brightness characteristics are also analyzed to detect images that are excessively bright or washed out.

---

## Noise Detection

Image characteristics are evaluated to identify excessive visual noise that can reduce image quality.

---

## Severe Degradation Detection

Multiple image-quality signals are considered to identify heavily degraded images.

---

## Potential Visual Defect Detection

The system also provides a potential visual-defect indicator based on available image-quality measurements.

This is intended as a general quality signal rather than a domain-specific industrial defect detector.

---

# 💯 Quality Score

Every analyzed image receives an overall quality score between:

```text
0 - 100
```

Higher scores indicate better overall image quality.

The quality score is calculated using the Machine Learning class probabilities.

Conceptually:

```text
ACCEPTABLE probability → high quality contribution
DEGRADED probability   → medium quality contribution
DEFECTIVE probability  → low quality contribution
```

---

# 🎯 ML Confidence

The application displays the confidence associated with the model's predicted class.

Example:

```text
Prediction:
ACCEPTABLE

Confidence:
52.1%
```

A higher confidence indicates that the classifier assigned a larger probability to its selected class.

---

# 📐 Score Uncertainty

VisionGuard also reports score uncertainty.

Example:

```text
Quality Score:
76.89

Score Uncertainty:
±26.59
```

The uncertainty is derived from the spread of the Machine Learning class-probability distribution across the quality-score levels.

It provides additional context about how strongly the model distinguishes between possible quality outcomes.

> Score uncertainty should not be interpreted as a statistically calibrated confidence interval.

---

# 🛠️ Technology Stack

## Frontend

- React
- Vite
- JavaScript
- HTML5
- CSS3
- Fetch API

## Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy

## Computer Vision

- OpenCV
- NumPy

## Machine Learning

- Scikit-learn
- Random Forest Classifier
- Joblib

## Database

- SQLite

## Development & Deployment

- Git
- GitHub
- Docker
- Docker Compose
- Nginx

---

# 📁 Project Structure

```text
image-quality-ai/
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── api/
│   │   │   └── routes.py
│   │   │
│   │   ├── cv/
│   │   │   └── features.py
│   │   │
│   │   ├── database/
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   │
│   │   ├── ml/
│   │   │   └── predictor.py
│   │   │
│   │   ├── services/
│   │   │   └── analyzer.py
│   │   │
│   │   └── main.py
│   │
│   ├── uploads/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   │
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

> The repository may contain additional model-training, dataset, configuration, and utility files.

---

# 🚀 Quick Start — Docker

The easiest way to run the complete VisionGuard application is with **Docker Compose**.

Docker starts both the frontend and backend services without requiring you to manually configure separate Python and Node.js environments.

---

## Prerequisites

Install:

- Git
- Docker Desktop

Make sure Docker Desktop is running before executing the commands below.

---

## 1. Clone the Repository

```bash
git clone https://github.com/JayasuryaRavipati/image-quality-ai.git
```

Enter the project:

```bash
cd image-quality-ai
```

---

## 2. Build and Start VisionGuard

Run:

```bash
docker compose up --build
```

Docker Compose will build and start the frontend and backend containers.

The first build may take several minutes because Docker needs to download and install the required dependencies.

---

## 3. Open the Application

Once the containers are running, open:

### Frontend

```text
http://localhost:8080
```

### Backend

```text
http://localhost:8000
```

### Swagger API Documentation

```text
http://localhost:8000/docs
```

### Backend Health Check

```text
http://localhost:8000/health
```

---

## 4. Check Container Status

Run:

```bash
docker compose ps
```

You should see the frontend and backend containers running.

---

## 5. Stop the Application

Press:

```text
Ctrl + C
```

in the terminal running Docker Compose.

Then run:

```bash
docker compose down
```

---

## Rebuild After Code Changes

If application code or dependencies change, rebuild the containers:

```bash
docker compose down
docker compose up --build
```

---

# 💻 Manual Installation

If you do not want to use Docker, the frontend and backend can also be started manually.

---

# 🐍 Backend Setup

## 1. Clone the Repository

```bash
git clone https://github.com/JayasuryaRavipati/image-quality-ai.git
```

Enter the project:

```bash
cd image-quality-ai
```

Move to the backend:

```bash
cd backend
```

---

## 2. Create a Python Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
```

Activate:

```bash
source venv/bin/activate
```

---

## 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Start the Backend

```bash
python -m uvicorn app.main:app --reload
```

The backend should now be available at:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

Keep this terminal running.

---

# ⚛️ Frontend Setup

Open a **new terminal** from the project root.

Move into the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The frontend should now be available at:

```text
http://localhost:5173
```

Open that address in your browser.

---

# 🧪 How to Use VisionGuard

After starting the application:

1. Open the VisionGuard frontend.
2. Click **Upload Image**.
3. Select a JPEG, PNG, or WEBP image.
4. Click **Analyze**.
5. Wait for the image-analysis pipeline to complete.
6. Review the overall quality score.
7. Review the quality classification.
8. Check the ML confidence and score uncertainty.
9. Review detected image-quality issues.
10. Review image statistics and ML probabilities.
11. Scroll to **Analysis History** to see previous results.
12. Click a history record to open its detailed inspection report.

---

# 📤 Supported Uploads

Supported formats:

```text
JPEG
PNG
WEBP
```

Supported MIME types:

```text
image/jpeg
image/png
image/webp
```

Maximum upload size:

```text
10 MB
```

---

# 🔌 REST API

FastAPI automatically provides interactive API documentation at:

```text
http://localhost:8000/docs
```

---

## Analyze an Image

```http
POST /api/analyze
```

Request type:

```text
multipart/form-data
```

Form field:

```text
file
```

Example with cURL:

```bash
curl -X POST \
  "http://127.0.0.1:8000/api/analyze" \
  -H "accept: application/json" \
  -F "file=@example.jpg;type=image/jpeg"
```

---

## Example Analysis Response

```json
{
  "id": 13,
  "filename": "example.jpg",
  "content_type": "image/jpeg",
  "image_url": "/api/history/13/image",
  "quality_score": 76.89,
  "quality_label": "ACCEPTABLE",
  "confidence": 0.5212,
  "score_uncertainty": 26.59,
  "processing_ms": 5055,
  "image": {
    "filename": "example.jpg",
    "content_type": "image/jpeg",
    "size_bytes": 6630,
    "width": 222,
    "height": 148,
    "format": "JPEG"
  },
  "analysis": {
    "quality_score": 76.89,
    "quality_label": "ACCEPTABLE",
    "confidence": 0.5212,
    "score_uncertainty": 26.59,
    "ml_prediction": {
      "label": "ACCEPTABLE",
      "confidence": 0.5212,
      "probabilities": {
        "ACCEPTABLE": 0.5212,
        "DEGRADED": 0.3798,
        "DEFECTIVE": 0.0989
      },
      "model_type": "RandomForestClassifier",
      "model_version": "1.0.0"
    }
  }
}
```

---

# 📜 Get Analysis History

```http
GET /api/history
```

Optional limit:

```text
/api/history?limit=20
```

The endpoint returns recent analysis records stored in SQLite.

---

# 🔎 Get Analysis Details

```http
GET /api/history/{analysis_id}
```

Example:

```text
/api/history/13
```

This endpoint returns the complete stored analysis for the selected record.

---

# 🖼️ Get Stored Analysis Image

```http
GET /api/history/{analysis_id}/image
```

Example:

```text
/api/history/13/image
```

This endpoint returns the original uploaded image associated with the selected analysis.

---

# ❤️ Health Check

```http
GET /health
```

Example:

```text
http://localhost:8000/health
```

This can be used to verify that the backend service is running.

---

# 📊 Example Analysis Result

A typical analysis can produce:

```text
Filename:            example.jpg

Quality Score:       76.89 / 100
Quality Label:       ACCEPTABLE

ML Confidence:       52.1%
Score Uncertainty:   ±26.59

Dimensions:          222 × 148
Format:              JPEG
File Size:           6.47 KB
Processing Time:     5055 ms

Detected Issues:
Noise - Low Severity
```

Example ML probabilities:

```text
ACCEPTABLE    52.12%
DEGRADED      37.98%
DEFECTIVE      9.89%
```

---

# 🔍 Example Quality Issue

An individual quality check can look like:

```json
{
  "noise": {
    "detected": true,
    "severity": "low",
    "confidence": 0.55
  }
}
```

The current analysis pipeline checks:

```text
blur
underexposure
overexposure
noise
severe_degradation
potential_visual_defect
```

---

# 💾 Database Persistence

VisionGuard uses:

```text
SQLite + SQLAlchemy
```

to store completed analyses.

Stored information includes:

- Filename
- Content type
- Image path
- File size
- Quality score
- Quality label
- ML confidence
- Score uncertainty
- Processing time
- Detected issues
- Image statistics
- ML prediction
- Analysis timestamp

Uploaded images are stored separately and linked to their corresponding database records.

---

# 🔐 Image Validation

Before analysis, the backend validates the uploaded file.

Validation includes:

### File Type

Only:

```text
JPEG
PNG
WEBP
```

are accepted.

### File Size

Maximum:

```text
10 MB
```

### Image Decoding

The backend attempts to decode the uploaded image before processing.

Empty, invalid, unsupported, or unreadable files are rejected with an appropriate HTTP error response.

---

# 💡 Why Computer Vision + Machine Learning?

A traditional threshold-only computer-vision system may detect individual quality characteristics, but it does not provide a learned overall quality decision.

VisionGuard combines:

```text
Computer Vision
       +
Feature Engineering
       +
Machine Learning
       =
Image Quality Classification
```

Computer Vision provides interpretable measurements such as:

- Sharpness
- Brightness
- Contrast
- Noise

Machine Learning combines these features to predict the overall image-quality class.

This allows the application to provide both:

```text
Interpretable quality measurements
+
Data-driven overall classification
```

---

# 🌲 Why Random Forest?

Random Forest was selected because it is suitable for structured numerical image features.

Advantages include:

- Handles non-linear relationships
- Works well with engineered numerical features
- Captures interactions between features
- Supports class-probability predictions
- Fast inference
- Relatively robust
- Easy to integrate into a Python backend
- Lightweight compared with large deep-learning architectures

---

# ⚡ Why FastAPI?

FastAPI provides:

- Python-based REST API development
- File upload handling
- Request validation
- Automatic OpenAPI generation
- Interactive Swagger documentation
- Simple integration with OpenCV
- Simple integration with Scikit-learn
- High development speed

---

# ⚛️ Why React?

React provides a responsive frontend for:

- Image upload
- Image preview
- Quality results
- ML confidence
- Score uncertainty
- Quality issue visualization
- ML probability visualization
- Image statistics
- Analysis history
- Detailed inspection reports

---

# 🚫 External AI Services

VisionGuard does **not** rely on external AI or Computer Vision APIs for image-quality analysis.

The Computer Vision processing and Machine Learning inference run within the application.

Therefore:

```text
No external AI API is required.
No external vision API is required.
No AI API key is required.
```

---

# ⚠️ Limitations

The current implementation has several limitations:

- Image quality is partly subjective.
- The model was trained using a limited dataset and degradation strategy.
- Performance may vary across different image domains.
- Prediction confidence does not guarantee correctness.
- Score uncertainty is derived from the classifier probability distribution and is not a calibrated statistical confidence interval.
- Potential visual-defect detection is a general quality indicator rather than a specialized industrial defect-detection model.
- Quality thresholds may require tuning for specific domains.
- Processing time depends on hardware and image size.

---

# 🔮 Future Improvements

Possible improvements include:

- CNN-based image-quality classification
- Transfer learning
- Deep-learning-based defect detection
- Defect localization
- Image heatmaps
- Explainable AI visualization
- Advanced anomaly detection
- Larger training datasets
- More diverse degradation types
- Probability calibration
- Batch image analysis
- Drag-and-drop multi-image upload
- User authentication
- PostgreSQL support
- Cloud object storage
- Model monitoring
- Automated model retraining
- CI/CD pipeline
- Cloud deployment

---

# 🧰 Troubleshooting

## Docker containers do not start

Check Docker Desktop and make sure it is running.

Then execute:

```bash
docker compose down
docker compose up --build
```

---

## Check container status

```bash
docker compose ps
```

---

## View Docker logs

```bash
docker compose logs
```

Backend logs:

```bash
docker compose logs backend
```

Frontend logs:

```bash
docker compose logs frontend
```

---

## Backend does not start manually

Make sure the virtual environment is activated.

Windows:

```bash
venv\Scripts\activate
```

Then reinstall dependencies:

```bash
pip install -r requirements.txt
```

Start the backend again:

```bash
python -m uvicorn app.main:app --reload
```

---

## Frontend does not start

Run:

```bash
npm install
npm run dev
```

---

## Verify Backend

Open:

```text
http://localhost:8000/health
```

or:

```text
http://localhost:8000/docs
```

If Swagger loads correctly, the backend is running.

---

# 🎓 Key Learning Outcomes

This project demonstrates practical experience with:

- Computer Vision
- Image Processing
- Feature Engineering
- Machine Learning Classification
- Model Training
- Model Evaluation
- Model Inference
- OpenCV
- Scikit-learn
- FastAPI
- React
- REST API Development
- SQLAlchemy
- SQLite
- Image Upload and Storage
- Full-Stack Integration
- Docker
- Docker Compose
- Nginx
- Git
- GitHub

---

# 👨‍💻 Author

**Jaya Surya Ravipati**

B.Tech — Information Technology

GitHub: `JayasuryaRavipati`

---

# 📄 Project Purpose

VisionGuard was developed as part of an **Internship Applicant Technical Assessment** focused on:

- Computer Vision
- Machine Learning / Deep Learning
- Backend Development
- Frontend Development
- Deployment

The objective was to build a working and deployable full-stack AI application that automatically evaluates image quality without relying on external AI or vision APIs.

---

# 🛡️ VisionGuard

### AI-Powered Image Quality & Defect Detection

Built with:

**React • FastAPI • OpenCV • Scikit-learn • SQLite • Docker**