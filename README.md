# VisionGuard — AI-Powered Image Quality & Defect Detection

VisionGuard is a full-stack AI-powered image quality assessment application that automatically analyzes uploaded images, detects common image-quality problems, and classifies the overall image quality as **ACCEPTABLE**, **DEGRADED**, or **DEFECTIVE**.

The project combines traditional computer vision techniques with a machine-learning decision component and provides a complete web interface, REST API, persistent analysis history, and Docker-based deployment.

---

## Features

- Upload and analyze images through a web interface
- Blur / insufficient sharpness detection
- Underexposure detection
- Overexposure detection
- Image noise estimation
- Corruption / severe degradation detection
- Potential visual defect detection
- AI-based overall quality classification
- Quality score from 0–100
- ML prediction confidence
- Score uncertainty estimation
- Image statistics and quality metrics
- Persistent analysis history
- Previous image preview
- Analysis processing-time tracking
- REST API using FastAPI
- SQLite persistence using SQLAlchemy
- Dockerized frontend and backend
- Nginx production frontend server and API reverse proxy
- No external AI or vision APIs required

---

## System Architecture

```text
                    ┌─────────────────────┐
                    │        User         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ React + Vite UI     │
                    │ Nginx in Docker     │
                    │ Port: 8081          │
                    └──────────┬──────────┘
                               │
                         /api requests
                               │
                               ▼
                    ┌─────────────────────┐
                    │ FastAPI Backend     │
                    │ Port: 8001          │
                    └──────────┬──────────┘
                               │
               ┌───────────────┼───────────────┐
               │               │               │
               ▼               ▼               ▼
       ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
       │ Computer     │ │ RandomForest │ │ SQLAlchemy + │
       │ Vision       │ │ ML Model     │ │ SQLite       │
       └──────────────┘ └──────────────┘ └──────────────┘
```

---

## Machine Learning Component

VisionGuard includes a **Random Forest classifier** as its AI-based decision component.

The model predicts one of three image-quality classes:

- `ACCEPTABLE`
- `DEGRADED`
- `DEFECTIVE`

### Model Features

The model uses nine numerical image features:

1. Width
2. Height
3. Aspect ratio
4. Sharpness
5. Brightness
6. Contrast
7. Noise
8. Intensity standard deviation
9. Number of unique intensity values

These features are extracted from the uploaded image before being passed to the trained classifier.

---

## Model Training

The model was trained using clean images from the **Caltech-101 dataset** together with synthetically degraded versions of the images.

Synthetic degradation was used to generate examples containing image-quality problems such as:

- Blur
- Exposure degradation
- Noise
- Severe quality degradation

A source-level train/test split was used to reduce the risk of closely related versions of the same source image appearing in both training and testing data.

### Dataset Split

| Dataset | Samples |
|---|---:|
| Training | 1040 |
| Testing | 260 |

---

## Model Performance

Evaluation on the held-out test set produced:

| Metric | Score |
|---|---:|
| Accuracy | 0.7231 |
| Precision | 0.7193 |
| Recall | 0.7231 |
| F1 Score | 0.7192 |

These metrics reflect the current trained model and are not intended to represent production-level performance.

---

## Image Analysis Pipeline

When an image is uploaded, VisionGuard performs the following pipeline:

```text
Image Upload
     │
     ▼
File Validation
     │
     ▼
Image Decoding
     │
     ▼
Feature Extraction
     │
     ├── Sharpness
     ├── Brightness
     ├── Contrast
     ├── Noise
     ├── Dimensions
     └── Intensity Statistics
     │
     ▼
Computer Vision Quality Checks
     │
     ▼
Random Forest Prediction
     │
     ▼
Quality Score Calculation
     │
     ▼
ACCEPTABLE / DEGRADED / DEFECTIVE
     │
     ▼
Store Analysis in SQLite
     │
     ▼
Return Result to Frontend
```

---

## Quality Score

The overall quality score is calculated using the class probabilities produced by the ML model.

```text
Quality Score =
    P(ACCEPTABLE) × 100
  + P(DEGRADED) × 60
  + P(DEFECTIVE) × 20
```

The resulting score is presented on a 0–100 scale.

---

## Confidence and Score Uncertainty

The ML confidence displayed by VisionGuard is the probability associated with the model's predicted class.

For example:

```text
Model confidence = 0.5212
Displayed confidence = 52.12%
```

VisionGuard also calculates a score uncertainty value based on the probability distribution across the three quality classes.

The uncertainty represents the standard deviation of the class-score distribution around the calculated quality score.

It should be interpreted as uncertainty in **quality-score points**, rather than as a calibrated statistical confidence interval.

---

## Computer Vision Analysis

### Blur / Sharpness

The application evaluates image sharpness to identify images that may be blurry or insufficiently focused.

### Underexposure

Brightness statistics are analyzed to identify images that are excessively dark.

### Overexposure

The intensity distribution is analyzed to detect excessively bright or washed-out images.

### Noise

Image statistics are used to estimate the presence of excessive image noise.

### Corruption / Severe Degradation

The backend validates whether an uploaded file can be successfully decoded as an image and evaluates extracted statistics for signs of severe degradation.

### Potential Visual Defects

Multiple quality signals and the ML prediction are combined to identify images that may contain significant visual-quality defects.

---

## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- CSS
- Nginx

### Backend

- Python
- FastAPI
- Uvicorn
- OpenCV
- Pillow
- NumPy

### Machine Learning

- Scikit-learn
- Random Forest
- Joblib

### Database

- SQLite
- SQLAlchemy

### Deployment

- Docker
- Docker Compose
- Nginx

---

## Project Structure

```text
visionguard/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py
│   │   │
│   │   ├── database/
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   │
│   │   ├── services/
│   │   │   └── analyzer.py
│   │   │
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── ...
│   │
│   ├── nginx.conf
│   ├── package.json
│   └── Dockerfile
│
├── ml/
│   └── models/
│       └── trained model files
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

# Running the Project with Docker

Docker Compose is the recommended way to run VisionGuard.

## Prerequisites

Install:

- Docker Desktop
- Git

Make sure Docker Desktop is running.

---

## 1. Clone the Repository

```bash
git clone https://github.com/JayasuryaRavipati/image-quality-ai.git
cd image-quality-ai
```

---

## 2. Build and Start the Application

```bash
docker compose up --build
```

Wait until the backend reports that Uvicorn is running and the frontend Nginx container has started.

---

## 3. Open the Application

### Frontend

```text
http://localhost:8081
```

### Backend API

```text
http://localhost:8000
```

### Swagger API Documentation

```text
http://localhost:8000/docs
```

### Health Endpoint

```text
http://localhost:8000/health
```

> **Important:** The Docker frontend is exposed on port **8081**.

---

## 4. Stop the Application

Press:

```text
Ctrl + C
```

Then run:

```bash
docker compose down
```

To remove Docker volumes as well:

```bash
docker compose down -v
```

---

# Running Without Docker

## Backend Setup

Open a terminal and move to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
python -m uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

Open another terminal:

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

Use the URL displayed by Vite in the terminal.

> The Vite development-server port and the Docker/Nginx frontend port are separate configurations. The Docker deployment uses **8081**.

---

# Using VisionGuard

1. Start the application.
2. Open the frontend.
3. Upload a supported image.
4. Click the analyze button.
5. Wait for the backend to process the image.
6. Review the quality score and classification.
7. Review detected quality issues.
8. Check ML confidence and image statistics.
9. Open the History section to review previous analyses.

---

# REST API

## Analyze Image

```http
POST /api/analyze
```

Uploads an image and performs image-quality analysis.

The result contains information such as:

```json
{
  "id": 1,
  "filename": "example.jpg",
  "content_type": "image/jpeg",
  "image_url": "/api/history/1/image",
  "quality_score": 76.89,
  "quality_label": "ACCEPTABLE",
  "confidence": 0.5212,
  "score_uncertainty": 26.59,
  "processing_ms": 5055
}
```

---

## Get Analysis History

```http
GET /api/history
```

Returns previously stored image-analysis records.

---

## Get Analysis Details

```http
GET /api/history/{analysis_id}
```

Returns detailed information for a specific analysis.

---

## Get Stored Image

```http
GET /api/history/{analysis_id}/image
```

Returns the image associated with a stored analysis record.

---

## Health Check

```http
GET /health
```

Used to verify that the backend service is running.

---

# Database Persistence

VisionGuard uses **SQLite** for local persistence and **SQLAlchemy** as the ORM layer.

Each analysis record can store:

- Filename
- Content type
- Stored image path
- File size
- Quality score
- Quality label
- ML confidence
- Score uncertainty
- Processing time
- Detected issues
- Image statistics
- ML prediction information
- Creation timestamp

SQLAlchemy provides the communication layer between the FastAPI application and SQLite.

---

# Nginx

In the Dockerized application, Nginx is used to:

- Serve the production React build
- Handle frontend requests
- Reverse proxy `/api` requests to the FastAPI backend

This allows the React frontend to communicate with the backend while both applications run as separate Docker services.

---

# Docker Architecture

The Docker setup contains two primary application containers:

```text
Browser
   │
   ▼
localhost:8081
   │
   ▼
Nginx / React Frontend
   │
   │ /api/*
   ▼
FastAPI Backend
   │
   ▼
Computer Vision + ML
   │
   ▼
SQLAlchemy
   │
   ▼
SQLite
```

Docker Compose manages the frontend, backend, networking, and persistent data volume.

---

# External AI Services

VisionGuard does **not** rely on external AI or computer-vision APIs.

Image processing and prediction are performed locally using:

- OpenCV
- NumPy
- Scikit-learn
- A locally trained Random Forest model

Therefore, no external AI API key is required.

---

# Design Decisions

### Why Random Forest?

Random Forest was selected because the current system uses structured numerical image-quality features.

It provides:

- Non-linear decision boundaries
- Multi-class classification
- Probability estimates
- Good performance on structured/tabular features
- Relatively fast CPU inference

### Why Combine ML and Computer Vision?

Traditional computer-vision metrics provide interpretable information such as brightness, sharpness, and noise.

The ML model provides an additional learned decision component that combines several extracted features to predict the overall quality class.

This hybrid design keeps the system interpretable while satisfying the requirement for an AI-based quality decision component.

### Why FastAPI?

FastAPI provides:

- Fast API development
- Request validation
- File-upload support
- Automatic Swagger documentation
- Good Python ML integration

### Why SQLAlchemy?

SQLAlchemy provides an ORM layer between FastAPI and SQLite and makes analysis records easier to create, query, and maintain.

### Why Nginx?

Nginx serves the optimized production frontend build and acts as the reverse proxy between the browser and FastAPI backend in the Docker environment.

---

# Limitations

The current implementation has several limitations:

- The model is trained on a limited dataset.
- Synthetic degradation may not represent every real-world defect.
- The Random Forest model operates on engineered numerical features rather than raw image pixels.
- The quality score is application-defined rather than an industry-standard perceptual quality score.
- Model confidence should not be interpreted as a fully calibrated statistical probability.
- Score uncertainty is based on the model class-probability distribution and is not a formal confidence interval.

---

# Future Improvements

Possible future improvements include:

- Train on a larger real-world defect dataset
- Add CNN-based image-quality classification
- Add defect localization
- Add segmentation for defective regions
- Add explainable visual heatmaps
- Improve probability calibration
- Add additional image-quality metrics
- Add authentication and user-specific history
- Add cloud deployment
- Add automated model retraining and evaluation pipelines
- Add database migrations for production schema management

---

# Troubleshooting

## Frontend Does Not Open

Confirm the containers are running:

```bash
docker compose ps
```

For the Docker deployment, open:

```text
http://localhost:8081
```

---

## Backend Does Not Respond

Check:

```text
http://localhost:8000/health
```

View backend logs:

```bash
docker compose logs backend
```

---

## Database Schema Problems

During development, if an old Docker volume contains an incompatible SQLite schema, stop the containers and remove the development volume:

```bash
docker compose down -v
```

Then rebuild and start:

```bash
docker compose up --build
```

> Removing the volume deletes locally stored analysis history, so this should only be done when resetting development data is acceptable.

---

## Rebuild Without Docker Cache

If Docker appears to be using stale application files:

```bash
docker compose build --no-cache
docker compose up
```

---

# Assessment Requirements Covered

| Requirement | Implementation |
|---|---|
| Blur detection | Computer vision sharpness analysis |
| Underexposure | Brightness/intensity analysis |
| Overexposure | Brightness/intensity analysis |
| Noise | Image noise estimation |
| Corruption / severe degradation | Validation and quality analysis |
| Potential visual defect | Combined CV + ML analysis |
| AI decision component | Random Forest classifier |
| Backend | FastAPI |
| Frontend | React + Vite |
| Database | SQLite + SQLAlchemy |
| Deployment | Docker + Nginx |
| External AI services | Not used |
| API keys | Not required |

---

# Author

**Jaya Surya Ravipati**  
B.Tech — Information Technology

GitHub: `JayasuryaRavipati`

---

## Repository

```text
https://github.com/JayasuryaRavipati/image-quality-ai
```

---

## License

This project was developed as part of an internship technical assessment and is intended primarily for educational and evaluation purposes.
