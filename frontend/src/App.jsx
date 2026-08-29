import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] =
    useState(false);

  const [showUploadModal, setShowUploadModal] =
    useState(false);

  const [selectedHistory, setSelectedHistory] =
    useState(null);

  const [showHistoryModal, setShowHistoryModal] =
    useState(false);

  const [
    historyDetailsLoading,
    setHistoryDetailsLoading,
  ] = useState(false);

  // =========================================================
  // HELPERS
  // =========================================================

  const formatLabel = (value) => {
    if (!value) {
      return "N/A";
    }

    return String(value)
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) =>
        letter.toUpperCase()
      );
  };

  const formatFileSize = (sizeBytes) => {
    if (
      sizeBytes === undefined ||
      sizeBytes === null
    ) {
      return "N/A";
    }

    const size = Number(sizeBytes);

    if (Number.isNaN(size)) {
      return "N/A";
    }

    if (size < 1024) {
      return `${size} B`;
    }

    if (size < 1024 * 1024) {
      return `${(
        size / 1024
      ).toFixed(2)} KB`;
    }

    return `${(
      size /
      (1024 * 1024)
    ).toFixed(2)} MB`;
  };

  const formatConfidence = (
    confidence
  ) => {
    if (
      confidence === undefined ||
      confidence === null
    ) {
      return "N/A";
    }

    const value = Number(
      confidence
    );

    if (Number.isNaN(value)) {
      return "N/A";
    }

    if (value <= 1) {
      return `${(
        value * 100
      ).toFixed(1)}%`;
    }

    return `${value.toFixed(
      1
    )}%`;
  };

  const getDetectedIssues = (
    issues
  ) => {
    if (!issues) {
      return [];
    }

    if (Array.isArray(issues)) {
      return issues;
    }

    return Object.entries(
      issues
    )
      .filter(
        ([, issue]) =>
          issue?.detected
      )
      .map(
        ([name, issue]) => ({
          name,
          ...issue,
        })
      );
  };

  const getIssueName = (
    issue,
    index = 0
  ) => {
    return (
      issue?.label ||
      issue?.name ||
      issue?.key ||
      `Issue ${index + 1}`
    );
  };

  const getFilename = (
    item
  ) => {
    return (
      item?.image?.filename ||
      item?.filename ||
      "Image"
    );
  };

  const normalizeHistory = (
    data
  ) => {
    if (Array.isArray(data)) {
      return data;
    }

    if (
      Array.isArray(
        data?.results
      )
    ) {
      return data.results;
    }

    if (
      Array.isArray(
        data?.items
      )
    ) {
      return data.items;
    }

    if (
      Array.isArray(
        data?.analyses
      )
    ) {
      return data.analyses;
    }

    if (
      Array.isArray(
        data?.data
      )
    ) {
      return data.data;
    }

    return [];
  };

  // =========================================================
  // SAFE JSON
  // =========================================================

  const parseResponse = async (
    response
  ) => {
    const text =
      await response.text();

    if (!text) {
      return null;
    }

    try {
      return JSON.parse(
        text
      );
    } catch {
      throw new Error(
        `Server returned invalid JSON. Status: ${response.status}`
      );
    }
  };

  // =========================================================
  // HISTORY
  // =========================================================

  const fetchHistory =
    async () => {
      try {
        setHistoryLoading(
          true
        );

        const response =
          await fetch(
            "/api/history"
          );

        const data =
          await parseResponse(
            response
          );

        if (!response.ok) {
          throw new Error(
            data?.detail ||
              `Could not load history. Status: ${response.status}`
          );
        }

        const items =
          normalizeHistory(
            data
          );

        setHistory(
          items
        );
      } catch (err) {
        console.error(
          "History error:",
          err
        );

        setHistory([]);
      } finally {
        setHistoryLoading(
          false
        );
      }
    };

  // =========================================================
  // HISTORY DETAILS
  // =========================================================

  const openHistoryDetails =
    async (item) => {
      setSelectedHistory(
        item
      );

      setShowHistoryModal(
        true
      );

      setHistoryDetailsLoading(
        true
      );

      try {
        const response =
          await fetch(
            `/api/history/${item.id}`
          );

        const data =
          await parseResponse(
            response
          );

        if (!response.ok) {
          throw new Error(
            data?.detail ||
              `Could not load analysis details. Status: ${response.status}`
          );
        }

        if (data) {
          setSelectedHistory(
            data
          );
        }
      } catch (err) {
        console.error(
          "History details error:",
          err
        );

        setSelectedHistory(
          item
        );
      } finally {
        setHistoryDetailsLoading(
          false
        );
      }
    };

  const closeHistoryDetails =
    () => {
      setShowHistoryModal(
        false
      );

      setSelectedHistory(
        null
      );

      setHistoryDetailsLoading(
        false
      );
    };

  // =========================================================
  // FILE
  // =========================================================

  const handleFileChange =
    (event) => {
      const selectedFile =
        event.target.files?.[0];

      setError("");

      if (!selectedFile) {
        return;
      }

      const allowedTypes = [
        "image/jpeg",
        "image/png",
        "image/webp",
      ];

      if (
        !allowedTypes.includes(
          selectedFile.type
        )
      ) {
        setError(
          "Please select a JPEG, PNG or WEBP image."
        );

        event.target.value =
          "";

        return;
      }

      const maxSize =
        10 *
        1024 *
        1024;

      if (
        selectedFile.size >
        maxSize
      ) {
        setError(
          "Image size must be less than 10 MB."
        );

        event.target.value =
          "";

        return;
      }

      if (preview) {
        URL.revokeObjectURL(
          preview
        );
      }

      setFile(
        selectedFile
      );

      setPreview(
        URL.createObjectURL(
          selectedFile
        )
      );

      event.target.value =
        "";
    };

  const clearSelectedImage =
    () => {
      if (preview) {
        URL.revokeObjectURL(
          preview
        );
      }

      setFile(null);
      setPreview(null);
      setError("");
    };

  // =========================================================
  // UPLOAD MODAL
  // =========================================================

  const openUploadModal =
    () => {
      setError("");
      setShowUploadModal(
        true
      );
    };

  const closeUploadModal =
    () => {
      if (loading) {
        return;
      }

      setShowUploadModal(
        false
      );

      setError("");
    };

  // =========================================================
  // ANALYZE
  // =========================================================

  const handleAnalyze =
    async () => {
      if (!file) {
        setError(
          "Please upload an image first."
        );

        return;
      }

      setLoading(true);
      setError("");
      setResult(null);

      try {
        const formData =
          new FormData();

        formData.append(
          "file",
          file
        );

        const response =
          await fetch(
            "/api/analyze",
            {
              method:
                "POST",
              body:
                formData,
            }
          );

        const data =
          await parseResponse(
            response
          );

        if (!response.ok) {
          throw new Error(
            data?.detail ||
              `Image analysis failed. Status: ${response.status}`
          );
        }

        if (!data) {
          throw new Error(
            "The server returned an empty response."
          );
        }

        const analysis = {
          ...data,
          ...(data.analysis ||
            {}),
        };

        if (
          analysis.quality_score ===
          undefined
        ) {
          throw new Error(
            "The server response does not contain quality analysis results."
          );
        }

        setResult(
          analysis
        );

        await fetchHistory();

        setShowUploadModal(
          false
        );
      } catch (err) {
        console.error(
          "Analysis error:",
          err
        );

        setError(
          err.message ||
            "Something went wrong while analyzing the image."
        );
      } finally {
        setLoading(
          false
        );
      }
    };

  // =========================================================
  // EFFECTS
  // =========================================================

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    return () => {
      if (preview) {
        URL.revokeObjectURL(
          preview
        );
      }
    };
  }, [preview]);

  // =========================================================
  // CURRENT RESULT
  // =========================================================

  const currentIssues =
    getDetectedIssues(
      result?.issues
    );

  const currentStatistics =
    Array.isArray(
      result?.statistics
    )
      ? result.statistics
      : null;

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="app">
      {/* HEADER */}

      <header className="header">
        <div className="header-content">
          <div className="brand">
            <div className="brand-icon">
              VG
            </div>

            <div>
              <h1>
                VisionGuard
              </h1>

              <p>
                AI-Powered
                Image Quality &
                Defect Detection
              </p>
            </div>
          </div>

          <div className="header-badge">
            AI Quality
            Inspector
          </div>
        </div>
      </header>

      <main className="container">
        {/* UPLOAD */}

        <section className="inspection-launch-card">
          <div className="inspection-launch-content">
            <p className="eyebrow">
              AI IMAGE
              INSPECTION
            </p>

            <h2>
              Inspect Image
              Quality & Defects
            </h2>

            <p className="inspection-launch-description">
              Analyze image
              sharpness,
              exposure, noise,
              degradation and
              potential visual
              defects using
              computer vision
              and machine
              learning.
            </p>

            <button
              type="button"
              className="open-upload-button"
              onClick={
                openUploadModal
              }
            >
              <span className="button-upload-icon">
                ↑
              </span>

              Upload Image
            </button>
          </div>
        </section>

        {/* CURRENT RESULTS */}

        {result && (
          <section className="results-section">
            <div className="result-top">
              <div className="score-panel">
                <div
                  className="score-circle"
                  style={{
                    "--score": `${
                      Number(
                        result.quality_score
                      ) * 3.6
                    }deg`,
                  }}
                >
                  <div className="score-inner">
                    <strong>
                      {Number(
                        result.quality_score
                      ).toFixed(
                        2
                      )}
                    </strong>

                    <span>
                      /100
                    </span>
                  </div>
                </div>

                <div>
                  <p className="result-label">
                    Overall
                    Quality
                  </p>

                  <div
                    className={`quality-badge ${
                      result.quality_label
                        ?.toLowerCase() ||
                      ""
                    }`}
                  >
                    {result.quality_label ||
                      "N/A"}
                  </div>
                </div>
              </div>

              <div className="summary-grid">
                <div className="summary-card">
                  <span>
                    ML Confidence
                  </span>

                  <strong>
                    {formatConfidence(
                      result.confidence
                    )}
                  </strong>
                </div>

                <div className="summary-card">
                  <span>
                    Score
                    Uncertainty
                  </span>

                  <strong>
                    {result.score_uncertainty !==
                      undefined &&
                    result.score_uncertainty !==
                      null
                      ? `±${Number(
                          result.score_uncertainty
                        ).toFixed(
                          1
                        )}`
                      : "N/A"}
                  </strong>
                </div>

                <div className="summary-card">
                  <span>
                    Detected
                    Issues
                  </span>

                  <strong>
                    {
                      currentIssues.length
                    }
                  </strong>
                </div>

                <div className="summary-card">
                  <span>
                    Model
                  </span>

                  <strong className="model-name">
                    {result
                      .ml_prediction
                      ?.model_type ||
                      "N/A"}
                  </strong>
                </div>
              </div>
            </div>

            {/* ISSUES */}

            <div className="section-card">
              <h3>
                Detected Issues
              </h3>

              {currentIssues.length >
              0 ? (
                <div className="issue-list">
                  {currentIssues.map(
                    (
                      issue,
                      index
                    ) => (
                      <div
                        key={
                          issue.name ||
                          index
                        }
                        className={`issue-item severity-${
                          issue.severity ||
                          "none"
                        }`}
                      >
                        <div>
                          <strong>
                            {getIssueName(
                              issue,
                              index
                            )
                              .replaceAll(
                                "_",
                                " "
                              )
                              .toUpperCase()}
                          </strong>

                          {issue.confidence !==
                            undefined && (
                            <p>
                              Confidence:{" "}
                              {formatConfidence(
                                issue.confidence
                              )}
                            </p>
                          )}
                        </div>

                        <span className="severity-badge">
                          {issue.severity
                            ? String(
                                issue.severity
                              ).toUpperCase()
                            : "DETECTED"}
                        </span>
                      </div>
                    )
                  )}
                </div>
              ) : (
                <div className="success-box">
                  No significant
                  quality issues
                  detected.
                </div>
              )}
            </div>

            {/* ML PROBABILITIES */}

            {result
              .ml_prediction
              ?.probabilities && (
              <div className="section-card">
                <h3>
                  AI Prediction
                  Probabilities
                </h3>

                <div className="probability-list">
                  {Object.entries(
                    result
                      .ml_prediction
                      .probabilities
                  ).map(
                    ([
                      label,
                      probability,
                    ]) => {
                      const value =
                        Number(
                          probability
                        );

                      const percent =
                        value <= 1
                          ? value *
                            100
                          : value;

                      return (
                        <div
                          key={
                            label
                          }
                          className="probability-item"
                        >
                          <div className="probability-header">
                            <span>
                              {
                                label
                              }
                            </span>

                            <strong>
                              {percent.toFixed(
                                1
                              )}
                              %
                            </strong>
                          </div>

                          <div className="progress-track">
                            <div
                              className={`progress-fill ${label.toLowerCase()}`}
                              style={{
                                width: `${Math.min(
                                  percent,
                                  100
                                )}%`,
                              }}
                            />
                          </div>
                        </div>
                      );
                    }
                  )}
                </div>
              </div>
            )}

            {/* STATISTICS */}

            <div className="section-card">
              <h3>
                Image
                Statistics
              </h3>

              <div className="statistics-grid">
                {currentStatistics
                  ? currentStatistics.map(
                      (stat) => (
                        <div
                          className="stat-card"
                          key={
                            stat.key
                          }
                        >
                          <span>
                            {stat.label ||
                              formatLabel(
                                stat.key
                              )}
                          </span>

                          <strong>
                            {typeof stat.value ===
                            "number"
                              ? stat.value.toFixed(
                                  2
                                )
                              : stat.value}
                          </strong>
                        </div>
                      )
                    )
                  : Object.entries(
                      result.image_statistics ||
                        {}
                    ).map(
                      ([
                        key,
                        value,
                      ]) => (
                        <div
                          className="stat-card"
                          key={
                            key
                          }
                        >
                          <span>
                            {formatLabel(
                              key
                            )}
                          </span>

                          <strong>
                            {typeof value ===
                            "number"
                              ? value.toFixed(
                                  2
                                )
                              : value}
                          </strong>
                        </div>
                      )
                    )}
              </div>
            </div>
          </section>
        )}

        {/* HISTORY */}

        <section className="history-section">
          <div className="history-header">
            <div>
              <p className="eyebrow">
                RECENT
                ANALYSES
              </p>

              <h2>
                Analysis
                History
              </h2>

              <p>
                Click any
                analysis to
                view complete
                details.
              </p>
            </div>

            <button
              type="button"
              className="refresh-button"
              onClick={
                fetchHistory
              }
              disabled={
                historyLoading
              }
            >
              {historyLoading
                ? "Refreshing..."
                : "Refresh"}
            </button>
          </div>

          {historyLoading &&
          history.length ===
            0 ? (
            <div className="empty-history">
              Loading
              analysis
              history...
            </div>
          ) : history.length ===
            0 ? (
            <div className="empty-history">
              <strong>
                No analysis
                history yet
              </strong>

              <p>
                Analyze your
                first image
                and the result
                will appear
                here.
              </p>
            </div>
          ) : (
            <div className="history-table-wrapper">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>
                      Image
                    </th>

                    <th>
                      Score
                    </th>

                    <th>
                      Status
                    </th>

                    <th>
                      ML
                      Confidence
                    </th>

                    <th>
                      Uncertainty
                    </th>

                    <th>
                      Issues
                    </th>

                    <th>
                      Analyzed
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {history.map(
                    (item) => {
                      const issues =
                        getDetectedIssues(
                          item.issues
                        );

                      return (
                        <tr
                          key={
                            item.id
                          }
                          className="clickable-history-row"
                          onClick={() =>
                            openHistoryDetails(
                              item
                            )
                          }
                        >
                          <td>
                            <div className="history-file">
                              <div className="file-icon">
                                IMG
                              </div>

                              <div>
                                <strong>
                                  {getFilename(
                                    item
                                  )}
                                </strong>

                                <span>
                                  ID #
                                  {
                                    item.id
                                  }
                                </span>
                              </div>
                            </div>
                          </td>

                          <td>
                            <strong className="history-score">
                              {Number(
                                item.quality_score
                              ).toFixed(
                                2
                              )}
                            </strong>

                            <span className="score-out-of">
                              /100
                            </span>
                          </td>

                          <td>
                            <span
                              className={`table-status ${
                                item.quality_label
                                  ?.toLowerCase() ||
                                ""
                              }`}
                            >
                              {item.quality_label ||
                                "N/A"}
                            </span>
                          </td>

                          <td>
                            {formatConfidence(
                              item.confidence
                            )}
                          </td>

                          <td>
                            {item.score_uncertainty !==
                              undefined &&
                            item.score_uncertainty !==
                              null
                              ? `±${Number(
                                  item.score_uncertainty
                                ).toFixed(
                                  1
                                )}`
                              : "N/A"}
                          </td>

                          <td>
                            {issues.length >
                            0 ? (
                              <div className="history-issues">
                                {issues
                                  .slice(
                                    0,
                                    2
                                  )
                                  .map(
                                    (
                                      issue,
                                      index
                                    ) => (
                                      <span
                                        key={
                                          issue.name ||
                                          index
                                        }
                                      >
                                        {getIssueName(
                                          issue,
                                          index
                                        )
                                          .replaceAll(
                                            "_",
                                            " "
                                          )
                                          .toUpperCase()}
                                      </span>
                                    )
                                  )}

                                {issues.length >
                                  2 && (
                                  <span>
                                    +
                                    {issues.length -
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
                    }
                  )}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>

      {/* UPLOAD MODAL */}

      {showUploadModal && (
        <div
          className="modal-overlay"
          onMouseDown={(
            event
          ) => {
            if (
              event.target ===
              event.currentTarget
            ) {
              closeUploadModal();
            }
          }}
        >
          <div className="inspection-modal">
            <div className="modal-header">
              <div>
                <p className="eyebrow">
                  IMAGE
                  INSPECTION
                </p>

                <h2>
                  Analyze Image
                  Quality
                </h2>

                <p>
                  Upload an
                  image to
                  inspect
                  quality and
                  potential
                  defects.
                </p>
              </div>

              <button
                type="button"
                className="modal-close-button"
                onClick={
                  closeUploadModal
                }
                disabled={
                  loading
                }
              >
                ×
              </button>
            </div>

            {!preview ? (
              <label className="modal-upload-box">
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={
                    handleFileChange
                  }
                />

                <div className="modal-upload-icon">
                  ↑
                </div>

                <strong>
                  Upload Image
                </strong>

                <p>
                  Drop an image
                  here or click
                  to browse
                </p>

                <span>
                  JPEG, PNG or
                  WEBP ·
                  Maximum 10 MB
                </span>
              </label>
            ) : (
              <div className="modal-preview-section">
                <div className="modal-preview-wrapper">
                  <img
                    src={
                      preview
                    }
                    alt="Selected"
                    className="modal-preview-image"
                  />
                </div>

                <div className="modal-file-details">
                  <div>
                    <span>
                      Selected
                      image
                    </span>

                    <strong>
                      {file?.name}
                    </strong>
                  </div>

                  <span className="modal-file-size">
                    {file
                      ? formatFileSize(
                          file.size
                        )
                      : ""}
                  </span>
                </div>
              </div>
            )}

            {error && (
              <div className="error-message modal-error">
                {error}
              </div>
            )}

            <div className="modal-actions">
              <label className="modal-secondary-button">
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={
                    handleFileChange
                  }
                  disabled={
                    loading
                  }
                />

                {file
                  ? "Change Image"
                  : "Upload"}
              </label>

              {file && (
                <button
                  type="button"
                  className="modal-remove-button"
                  onClick={
                    clearSelectedImage
                  }
                  disabled={
                    loading
                  }
                >
                  Remove
                </button>
              )}

              <button
                type="button"
                className="modal-analyze-button"
                onClick={
                  handleAnalyze
                }
                disabled={
                  loading ||
                  !file
                }
              >
                {loading ? (
                  <>
                    <span className="spinner" />
                    Analyzing...
                  </>
                ) : (
                  "Analyze"
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* HISTORY DETAILS MODAL */}

      {showHistoryModal &&
        selectedHistory && (
          <div
            className="modal-overlay history-modal-overlay"
            onMouseDown={(
              event
            ) => {
              if (
                event.target ===
                event.currentTarget
              ) {
                closeHistoryDetails();
              }
            }}
          >
            <div className="history-details-modal">
              <div className="history-details-header">
                <div>
                  <p className="eyebrow">
                    ANALYSIS
                    DETAILS
                  </p>

                  <h2>
                    Image
                    Inspection
                    Report
                  </h2>
                </div>

                <button
                  type="button"
                  className="modal-close-button"
                  onClick={
                    closeHistoryDetails
                  }
                >
                  ×
                </button>
              </div>

              {historyDetailsLoading && (
                <div className="history-details-loading">
                  Loading full
                  analysis
                  details...
                </div>
              )}

              <div className="history-details-split">
                {/* IMAGE */}

                <div className="history-image-panel">
                  <div className="history-image-preview">
                    {selectedHistory.image_url ? (
                      <img
                        src={
                          selectedHistory.image_url
                        }
                        alt={
                          getFilename(
                            selectedHistory
                          )
                        }
                        className="history-preview-img"
                      />
                    ) : (
                      <div className="history-image-placeholder">
                        <div>
                          IMG
                        </div>

                        <p>
                          Image
                          preview is
                          unavailable.
                        </p>
                      </div>
                    )}
                  </div>

                  <div className="history-image-info">
                    <strong>
                      {getFilename(
                        selectedHistory
                      )}
                    </strong>

                    <span>
                      Analysis ID:{" "}
                      {
                        selectedHistory.id
                      }
                    </span>
                  </div>
                </div>

                {/* SUMMARY */}

                <div className="history-summary-panel">
                  <div className="history-summary-heading">
                    <span>
                      ANALYSIS
                      SUMMARY
                    </span>
                  </div>

                  <div className="history-detail-score">
                    <div>
                      <span>
                        Quality
                        Score
                      </span>

                      <strong>
                        {Number(
                          selectedHistory.quality_score
                        ).toFixed(
                          2
                        )}
                      </strong>
                    </div>

                    <span
                      className={`table-status ${
                        selectedHistory.quality_label
                          ?.toLowerCase() ||
                        ""
                      }`}
                    >
                      {selectedHistory.quality_label ||
                        "N/A"}
                    </span>
                  </div>

                  <div className="history-detail-grid">
                    <div className="history-detail-card">
                      <span>
                        ML
                        Confidence
                      </span>

                      <strong>
                        {formatConfidence(
                          selectedHistory.confidence
                        )}
                      </strong>
                    </div>

                    <div className="history-detail-card">
                      <span>
                        Score
                        Uncertainty
                      </span>

                      <strong>
                        {selectedHistory.score_uncertainty !==
                          undefined &&
                        selectedHistory.score_uncertainty !==
                          null
                          ? `±${Number(
                              selectedHistory.score_uncertainty
                            ).toFixed(
                              1
                            )}`
                          : "N/A"}
                      </strong>
                    </div>

                    <div className="history-detail-card">
                      <span>
                        Dimensions
                      </span>

                      <strong>
                        {selectedHistory
                          .image
                          ?.width !=
                          null &&
                        selectedHistory
                          .image
                          ?.height !=
                          null
                          ? `${selectedHistory.image.width} × ${selectedHistory.image.height}`
                          : selectedHistory
                              .image_statistics
                              ?.width !=
                              null &&
                            selectedHistory
                              .image_statistics
                              ?.height !=
                              null
                          ? `${selectedHistory.image_statistics.width} × ${selectedHistory.image_statistics.height}`
                          : "N/A"}
                      </strong>
                    </div>

                    <div className="history-detail-card">
                      <span>
                        Format
                      </span>

                      <strong>
                        {selectedHistory
                          .image
                          ?.format ||
                          selectedHistory.content_type
                            ?.replace(
                              "image/",
                              ""
                            )
                            ?.toUpperCase() ||
                          "N/A"}
                      </strong>
                    </div>

                    <div className="history-detail-card">
                      <span>
                        File Size
                      </span>

                      <strong>
                        {formatFileSize(
                          selectedHistory
                            .image
                            ?.size_bytes
                        )}
                      </strong>
                    </div>

                    <div className="history-detail-card">
                      <span>
                        Processing
                      </span>

                      <strong>
                        {selectedHistory.processing_ms !==
                          undefined &&
                        selectedHistory.processing_ms !==
                          null
                          ? `${selectedHistory.processing_ms} ms`
                          : "N/A"}
                      </strong>
                    </div>

                    <div className="history-detail-card">
                      <span>
                        Model
                      </span>

                      <strong>
                        {selectedHistory
                          .ml_prediction
                          ?.model_type ||
                          "N/A"}
                      </strong>
                    </div>
                  </div>

                  <div className="history-analysis-date">
                    <span>
                      Analyzed
                    </span>

                    <strong>
                      {selectedHistory.created_at
                        ? new Date(
                            selectedHistory.created_at
                          ).toLocaleString()
                        : "N/A"}
                    </strong>
                  </div>
                </div>
              </div>

              {/* ISSUES */}

              <div className="history-modal-section">
                <div className="history-modal-section-title">
                  <p className="eyebrow">
                    QUALITY CHECK
                  </p>

                  <h3>
                    Detected
                    Issues
                  </h3>
                </div>

                {getDetectedIssues(
                  selectedHistory.issues
                ).length >
                0 ? (
                  <div className="history-modal-issues">
                    {getDetectedIssues(
                      selectedHistory.issues
                    ).map(
                      (
                        issue,
                        index
                      ) => (
                        <div
                          className="history-modal-issue"
                          key={
                            issue.name ||
                            index
                          }
                        >
                          <div>
                            <strong>
                              {getIssueName(
                                issue,
                                index
                              )
                                .replaceAll(
                                  "_",
                                  " "
                                )
                                .toUpperCase()}
                            </strong>

                            {issue.confidence !==
                              undefined && (
                              <p>
                                Confidence:{" "}
                                {formatConfidence(
                                  issue.confidence
                                )}
                              </p>
                            )}
                          </div>

                          {issue.severity && (
                            <span
                              className={`severity-badge severity-${String(
                                issue.severity
                              ).toLowerCase()}`}
                            >
                              {String(
                                issue.severity
                              ).toUpperCase()}
                            </span>
                          )}
                        </div>
                      )
                    )}
                  </div>
                ) : (
                  <div className="success-box">
                    No significant
                    quality issues
                    detected.
                  </div>
                )}
              </div>

              {/* STATISTICS */}

              <div className="history-modal-section">
                <div className="history-modal-section-title">
                  <p className="eyebrow">
                    TECHNICAL
                    METRICS
                  </p>

                  <h3>
                    Image
                    Statistics
                  </h3>
                </div>

                <div className="history-statistics-grid">
                  {Object.entries(
                    selectedHistory.image_statistics ||
                      {}
                  ).map(
                    ([
                      key,
                      value,
                    ]) => (
                      <div
                        className="history-stat-card"
                        key={
                          key
                        }
                      >
                        <span>
                          {formatLabel(
                            key
                          )}
                        </span>

                        <strong>
                          {typeof value ===
                          "number"
                            ? value.toFixed(
                                2
                              )
                            : value}
                        </strong>
                      </div>
                    )
                  )}
                </div>
              </div>

              {/* FOOTER */}

              <div className="history-modal-footer">
                <div>
                  <span>
                    Analysis ID
                  </span>

                  <strong>
                    {
                      selectedHistory.id
                    }
                  </strong>
                </div>

                <button
                  type="button"
                  className="history-close-button"
                  onClick={
                    closeHistoryDetails
                  }
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
    </div>
  );
}

export default App;