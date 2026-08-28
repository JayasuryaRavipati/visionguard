import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    setResult(null);
    setError("");

    if (!selectedFile) {
      setFile(null);
      setPreview(null);
      return;
    }

    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
  };

  const fetchHistory = async () => {
    try {
      setHistoryLoading(true);

     const response = await fetch(
  "/api/history"
);

      if (!response.ok) {
        throw new Error("Could not load history.");
      }

      const data = await response.json();

      setHistory(data.results || []);
    } catch (err) {
      console.error(err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError("Please select an image first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
  "/api/analyze",
  {
    method: "POST",
    body: formData,
  }
);

      if (!response.ok) {
        const errorData = await response.json();

        throw new Error(
          errorData.detail || "Image analysis failed."
        );
      }

      const data = await response.json();

      setResult(data.analysis);

      await fetchHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="brand">
            <div className="brand-icon">
              VG
            </div>

            <div>
              <h1>VisionGuard</h1>

              <p>
                AI-Powered Image Quality & Defect Detection
              </p>
            </div>
          </div>

          <div className="header-badge">
            AI Quality Inspector
          </div>
        </div>
      </header>

      <main className="container">
        {/* Upload Section */}

        <section className="upload-card">
          <div className="upload-heading">
            <div>
              <p className="eyebrow">
                IMAGE INSPECTION
              </p>

              <h2>
                Analyze Image Quality
              </h2>

              <p className="upload-description">
                Upload an image to detect blur,
                exposure problems, noise and severe
                visual degradation using computer
                vision and machine learning.
              </p>
            </div>
          </div>

          <label className="upload-box">
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileChange}
            />

            <div className="upload-icon">
              ↑
            </div>

            <strong>
              {file
                ? file.name
                : "Drop an image here or click to browse"}
            </strong>

            <span>
              JPEG, PNG or WEBP · Maximum 10 MB
            </span>
          </label>

          {preview && (
            <div className="selected-image-card">
              <div className="preview-wrapper">
                <img
                  src={preview}
                  alt="Selected preview"
                  className="preview-image"
                />
              </div>

              <div className="selected-image-info">
                <span>
                  Selected image
                </span>

                <strong>
                  {file?.name}
                </strong>

                <small>
                  {file
                    ? `${(
                        file.size /
                        (1024 * 1024)
                      ).toFixed(2)} MB`
                    : ""}
                </small>
              </div>
            </div>
          )}

          <button
            className="analyze-button"
            onClick={handleAnalyze}
            disabled={loading || !file}
          >
            {loading ? (
              <>
                <span className="spinner" />
                Analyzing Image...
              </>
            ) : (
              "Analyze Image"
            )}
          </button>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
        </section>

        {/* Result Section */}

        {result && (
          <section className="results-section">
            <div className="result-top">
              <div className="score-panel">
                <div
                  className="score-circle"
                  style={{
                    "--score": `${
                      result.quality_score * 3.6
                    }deg`,
                  }}
                >
                  <div className="score-inner">
                    <strong>
                      {result.quality_score}
                    </strong>

                    <span>
                      /100
                    </span>
                  </div>
                </div>

                <div>
                  <p className="result-label">
                    Overall Quality
                  </p>

                  <div
                    className={`quality-badge ${
                      result.quality_label?.toLowerCase()
                    }`}
                  >
                    {result.quality_label}
                  </div>
                </div>
              </div>

              <div className="summary-grid">
                <div className="summary-card">
                  <span>
                    ML Confidence
                  </span>

                  <strong>
                    {result.confidence !== undefined
                      ? `${(
                          result.confidence * 100
                        ).toFixed(1)}%`
                      : "N/A"}
                  </strong>
                </div>

                <div className="summary-card">
                  <span>
                    Detected Issues
                  </span>

                  <strong>
                    {
                      Object.values(
                        result.issues || {}
                      ).filter(
                        (issue) =>
                          issue.detected
                      ).length
                    }
                  </strong>
                </div>

                <div className="summary-card">
                  <span>
                    Model
                  </span>

                  <strong className="model-name">
                    {result.ml_prediction
                      ?.model_type || "N/A"}
                  </strong>
                </div>
              </div>
            </div>

            {/* Issues */}

            <div className="section-card">
              <h3>
                Detected Issues
              </h3>

              {Object.entries(
                result.issues || {}
              ).filter(
                ([, issue]) =>
                  issue.detected
              ).length > 0 ? (
                <div className="issue-list">
                  {Object.entries(
                    result.issues || {}
                  )
                    .filter(
                      ([, issue]) =>
                        issue.detected
                    )
                    .map(
                      ([name, issue]) => (
                        <div
                          key={name}
                          className={`issue-item severity-${issue.severity}`}
                        >
                          <div>
                            <strong>
                              {name
                                .replaceAll(
                                  "_",
                                  " "
                                )
                                .toUpperCase()}
                            </strong>

                            <p>
                              Confidence:{" "}
                              {(
                                issue.confidence *
                                100
                              ).toFixed(1)}
                              %
                            </p>
                          </div>

                          <span className="severity-badge">
                            {issue.severity?.toUpperCase()}
                          </span>
                        </div>
                      )
                    )}
                </div>
              ) : (
                <div className="success-box">
                  No significant quality issues
                  detected.
                </div>
              )}
            </div>

            {/* Probabilities */}

            {result.ml_prediction
              ?.probabilities && (
              <div className="section-card">
                <h3>
                  AI Prediction Probabilities
                </h3>

                <div className="probability-list">
                  {Object.entries(
                    result.ml_prediction
                      .probabilities
                  ).map(
                    ([
                      label,
                      probability,
                    ]) => (
                      <div
                        className="probability-item"
                        key={label}
                      >
                        <div className="probability-header">
                          <span>
                            {label}
                          </span>

                          <strong>
                            {(
                              probability *
                              100
                            ).toFixed(1)}
                            %
                          </strong>
                        </div>

                        <div className="progress-track">
                          <div
                            className={`progress-fill ${label.toLowerCase()}`}
                            style={{
                              width: `${
                                probability *
                                100
                              }%`,
                            }}
                          />
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}

            {/* Statistics */}

            <div className="section-card">
              <h3>
                Image Statistics
              </h3>

              <div className="statistics-grid">
                {Object.entries(
                  result.image_statistics ||
                    {}
                ).map(([key, value]) => (
                  <div
                    className="stat-card"
                    key={key}
                  >
                    <span>
                      {key
                        .replaceAll(
                          "_",
                          " "
                        )
                        .replace(
                          /\b\w/g,
                          (letter) =>
                            letter.toUpperCase()
                        )}
                    </span>

                    <strong>
                      {typeof value ===
                      "number"
                        ? value.toFixed(2)
                        : value}
                    </strong>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* History Section */}

        <section className="history-section">
          <div className="history-header">
            <div>
              <p className="eyebrow">
                RECENT ANALYSES
              </p>

              <h2>
                Analysis History
              </h2>

              <p>
                Review previously analyzed images
                and their quality results.
              </p>
            </div>

            <button
              className="refresh-button"
              onClick={fetchHistory}
              disabled={historyLoading}
            >
              {historyLoading
                ? "Refreshing..."
                : "Refresh"}
            </button>
          </div>

          {historyLoading &&
          history.length === 0 ? (
            <div className="empty-history">
              Loading analysis history...
            </div>
          ) : history.length === 0 ? (
            <div className="empty-history">
              <strong>
                No analysis history yet
              </strong>

              <p>
                Analyze your first image and the
                result will appear here.
              </p>
            </div>
          ) : (
            <div className="history-table-wrapper">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Image</th>
                    <th>Score</th>
                    <th>Status</th>
                    <th>Confidence</th>
                    <th>Issues</th>
                    <th>Analyzed</th>
                  </tr>
                </thead>

                <tbody>
                  {history.map((item) => {
                    const detectedIssues =
                      Object.entries(
                        item.issues || {}
                      ).filter(
                        ([, issue]) =>
                          issue.detected
                      );

                    return (
                      <tr key={item.id}>
                        <td>
                          <div className="history-file">
                            <div className="file-icon">
                              IMG
                            </div>

                            <div>
                              <strong>
                                {item.filename ||
                                  "Image"}
                              </strong>

                              <span>
                                ID #{item.id}
                              </span>
                            </div>
                          </div>
                        </td>

                        <td>
                          <strong className="history-score">
                            {Number(
                              item.quality_score
                            ).toFixed(2)}
                          </strong>

                          <span className="score-out-of">
                            /100
                          </span>
                        </td>

                        <td>
                          <span
                            className={`table-status ${
                              item.quality_label?.toLowerCase()
                            }`}
                          >
                            {
                              item.quality_label
                            }
                          </span>
                        </td>

                        <td>
                          {item.confidence !==
                            undefined &&
                          item.confidence !==
                            null
                            ? `${(
                                item.confidence *
                                100
                              ).toFixed(1)}%`
                            : "N/A"}
                        </td>

                        <td>
                          {detectedIssues.length >
                          0 ? (
                            <div className="history-issues">
                              {detectedIssues
                                .slice(0, 2)
                                .map(
                                  ([name]) => (
                                    <span
                                      key={
                                        name
                                      }
                                    >
                                      {name
                                        .replaceAll(
                                          "_",
                                          " "
                                        )
                                        .toUpperCase()}
                                    </span>
                                  )
                                )}

                              {detectedIssues.length >
                                2 && (
                                <span>
                                  +
                                  {detectedIssues.length -
                                    2}
                                </span>
                              )}
                            </div>
                          ) : (
                            <span className="no-issues">
                              None
                            </span>
                          )}
                        </td>

                        <td className="history-date">
                          {item.created_at
                            ? new Date(
                                item.created_at
                              ).toLocaleString()
                            : "N/A"}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;