# VisionGuard — Model Evaluation Report

## 1. Overview

VisionGuard is an AI-powered image quality and defect detection system designed to classify images into three overall quality categories:

- ACCEPTABLE
- DEGRADED
- DEFECTIVE

The system combines traditional computer-vision measurements with a machine-learning classifier.

The computer-vision layer extracts interpretable image-quality features, while a Random Forest classifier performs the final overall quality classification.

---

## 2. Dataset

Clean source images were obtained from the Caltech-101 image dataset.

Before generating degraded images, the original source images were divided into training and testing groups.

### Original Source Split

- Total selected clean source images: 100
- Training source images: 80
- Testing source images: 20

The split was performed before synthetic degradation was applied.

This helps prevent different degraded versions of the same original image from appearing in both the training and testing datasets.

---

## 3. Synthetic Image Degradation

Controlled image degradations were applied to the clean source images to create examples representing different image-quality conditions.

### ACCEPTABLE

Examples include:

- Original clean images
- Mild brightness variations

### DEGRADED

Examples include:

- Moderate blur
- Moderate image noise
- Underexposure
- Overexposure
- JPEG compression degradation

### DEFECTIVE

Examples include:

- Severe blur
- Severe noise
- Extreme underexposure
- Extreme overexposure
- Heavy compression
- Combined severe degradation

---

## 4. Dataset Size

The generated training dataset contains:

- ACCEPTABLE: 160 images
- DEGRADED: 400 images
- DEFECTIVE: 480 images
- Total training samples: 1,040

The testing dataset contains:

- ACCEPTABLE: 40 images
- DEGRADED: 100 images
- DEFECTIVE: 120 images
- Total testing samples: 260

---

## 5. Image Features

Nine interpretable features are extracted from each image:

1. Width
2. Height
3. Aspect ratio
4. Sharpness
5. Brightness
6. Contrast
7. Noise
8. Intensity standard deviation
9. Number of unique intensity values

These features represent measurable properties associated with image quality.

For example:

- Sharpness helps identify blur.
- Brightness helps identify underexposure and overexposure.
- Noise measurements help identify noisy images.
- Intensity statistics help identify severe degradation.

---

## 6. Machine-Learning Model

The overall quality classifier uses:

**RandomForestClassifier**

Main configuration:

- Number of trees: 300
- Minimum samples split: 4
- Minimum samples leaf: 2
- Class weighting: balanced
- Random state: 42

Random Forest was selected because it works effectively with structured numerical features and provides feature-importance information that improves model explainability.

---

## 7. Evaluation Results

The trained model was evaluated using the held-out test dataset containing 260 synthetically degraded images generated from source images excluded from training.

### Overall Metrics

| Metric | Result |
|---|---:|
| Accuracy | 72.31% |
| Weighted Precision | 71.93% |
| Weighted Recall | 72.31% |
| Weighted F1 Score | 71.92% |

The model therefore achieved approximately 72% classification accuracy on the current held-out synthetic evaluation dataset.

---

## 8. Confusion Matrix

The confusion matrix was:

| Actual \ Predicted | ACCEPTABLE | DEGRADED | DEFECTIVE |
|---|---:|---:|---:|
| ACCEPTABLE | 14 | 22 | 4 |
| DEGRADED | 11 | 76 | 13 |
| DEFECTIVE | 7 | 15 | 98 |

The generated visualization is available at:

`reports/confusion_matrix.png`

### Interpretation

The model performs best at recognizing DEFECTIVE images.

Out of 120 defective test images, 98 were correctly classified as DEFECTIVE.

The DEGRADED class also performs reasonably well, with 76 out of 100 samples correctly classified.

The largest difficulty occurs between ACCEPTABLE and DEGRADED images.

Only 14 of the 40 ACCEPTABLE samples were classified correctly, while 22 were classified as DEGRADED.

This indicates that mild quality changes can overlap with the characteristics of moderately degraded images.

---

## 9. Feature Importance

Random Forest feature importance produced the following ranking:

| Feature | Importance |
|---|---:|
| Sharpness | 0.2251 |
| Noise | 0.1825 |
| Unique intensity values | 0.1730 |
| Brightness | 0.1379 |
| Contrast | 0.1019 |
| Intensity standard deviation | 0.1018 |
| Aspect ratio | 0.0354 |
| Height | 0.0258 |
| Width | 0.0167 |

The generated visualization is available at:

`reports/feature_importance.png`

### Interpretation

Sharpness is the most influential feature in the current model.

Noise and unique intensity values are also highly influential.

This is reasonable because blur, noise, compression, exposure problems, and severe degradation directly affect these image statistics.

Image dimensions and aspect ratio have considerably lower importance.

---

## 10. Computer Vision + Machine Learning

VisionGuard uses a hybrid approach.

### Computer Vision Layer

OpenCV-based analysis measures:

- Blur/sharpness
- Brightness
- Contrast
- Noise
- Intensity distribution
- Severe image degradation

Rule-based thresholds are also used to provide interpretable issue-level severity information.

### Machine-Learning Layer

The extracted numerical image features are provided to the trained Random Forest classifier.

The classifier predicts:

- ACCEPTABLE
- DEGRADED
- DEFECTIVE

It also provides class probabilities used by the application to display ML confidence and calculate the overall quality score.

This architecture keeps individual defect detection interpretable while still using a learned model for the overall quality decision.

---

## 11. Explainability

VisionGuard provides several forms of explainability.

### Image Statistics

The API returns measurements including:

- Sharpness
- Brightness
- Contrast
- Noise
- Intensity standard deviation
- Unique intensity values

### Issue Severity

Detected quality issues include severity levels such as:

- LOW
- MEDIUM
- HIGH

### Prediction Probabilities

The frontend displays the Random Forest probabilities for:

- ACCEPTABLE
- DEGRADED
- DEFECTIVE

### Feature Importance

Random Forest feature importance shows which measurements have the greatest influence on the learned classifier.

---

## 12. Failure Cases

The confusion matrix shows that the largest source of error is distinguishing ACCEPTABLE images from DEGRADED images.

This can happen because mild blur, brightness changes, compression, or noise may produce feature values close to those of clean images.

Natural characteristics of an image can also affect the extracted statistics. For example, an intentionally dark photograph may have brightness characteristics similar to an underexposed image.

Similarly, naturally smooth regions may produce different sharpness statistics even when the image is visually acceptable.

---

## 13. Limitations

The current model has several limitations.

1. The training and test samples are generated primarily using controlled synthetic degradations.

2. Performance on real-world image-quality datasets may differ from the reported test results.

3. The current model uses nine engineered image features rather than features learned directly from image pixels by a deep neural network.

4. Some image characteristics are content-dependent. Dark scenes, smooth surfaces, or artistic blur can influence quality measurements.

5. Issue-level confidence values are derived from severity rules rather than separately trained probabilistic defect classifiers.

6. The current evaluation should not be interpreted as proof of approximately 72% accuracy on arbitrary real-world or out-of-distribution images.

---

## 14. Future Improvements

Potential improvements include:

- Training with larger real-world image-quality datasets
- Adding more clean source images
- Adding additional degradation types
- Training dedicated classifiers for individual defects
- Probability calibration
- CNN-based image feature extraction
- Transfer learning
- Localized defect detection
- Heatmap visualization
- More extensive out-of-distribution evaluation
- Hyperparameter optimization

---

## 15. Conclusion

VisionGuard demonstrates a complete hybrid computer-vision and machine-learning approach to image quality assessment.

The current Random Forest model achieved:

- 72.31% accuracy
- 71.93% weighted precision
- 72.31% weighted recall
- 71.92% weighted F1 score

on the current held-out synthetic evaluation dataset.

The system combines interpretable image statistics, defect detection rules, machine-learning classification, confidence information, persistence, and a full-stack user interface.

The current results provide a reproducible baseline while clearly identifying opportunities for further improvement on larger and more diverse real-world datasets.