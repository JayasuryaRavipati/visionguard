# VisionGuard

## AI-Powered Image Quality & Defect Detection

VisionGuard is a full-stack computer vision and machine-learning application that automatically evaluates the visual quality of uploaded images.

The system detects common image-quality problems such as blur, exposure problems, image noise, severe degradation, and potential visual defects. It also uses a trained machine-learning model to classify the overall image quality as:

- ACCEPTABLE
- DEGRADED
- DEFECTIVE

---

## Features

### Image Quality Detection

VisionGuard analyzes uploaded images for:

- Blur / insufficient sharpness
- Underexposure
- Overexposure
- Image noise
- Severe image degradation
- Potential visual defects

### AI-Based Quality Classification

A trained Random Forest classifier predicts the overall image quality using computer-vision features extracted from the image.

The model returns:

- Quality label
- Quality score
- Prediction confidence
- Class probabilities

### Explainable Results

The application displays interpretable image statistics including:

- Sharpness
- Brightness
- Contrast
- Noise
- Intensity standard deviation
- Unique intensity values
- Image dimensions

### Analysis History

Analysis results are stored in a SQLite database.

Users can review previous analyses including:

- Filename
- Quality score
- Quality label
- ML confidence
- Detected issues
- Analysis timestamp

---

# System Architecture

VisionGuard uses a hybrid Computer Vision + Machine Learning architecture.

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
                             ▼
                    ┌─────────────────┐
                    │ Quality Result  │
                    └────────┬────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
          ┌──────────────┐      ┌──────────────┐
          │   SQLite     │      │   Frontend   │
          │ Persistence  │      │ Visualization│
          └──────────────┘      └──────────────┘