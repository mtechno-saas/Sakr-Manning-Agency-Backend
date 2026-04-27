import React, { useState, useCallback } from "react";
import useAI from "../../../../hooks/dashboard/useAI";
import { ASSETS } from "../../../../utils/constants";

const DocumentUploadModal = ({ isOpen, onClose, onSuccess, scale = 1 }) => {
  const { uploadDocument, loading } = useAI();
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [extractedData, setExtractedData] = useState(null);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (validateFile(droppedFile)) {
        setFile(droppedFile);
      }
    }
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
      }
    }
  };

  const validateFile = (file) => {
    const validTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!validTypes.includes(file.type)) {
      alert("Please upload a PDF or DOCX file");
      return false;
    }

    if (file.size > maxSize) {
      alert("File size must be less than 10MB");
      return false;
    }

    return true;
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploadProgress(10);

    const result = await uploadDocument(file);

    if (result) {
      setUploadProgress(100);
      setExtractedData(result.extracted_data);

      // Show success for 2 seconds, then close
      setTimeout(() => {
        onSuccess?.(result);
        handleClose();
      }, 2000);
    } else {
      setUploadProgress(0);
    }
  };

  const handleClose = () => {
    setFile(null);
    setUploadProgress(0);
    setExtractedData(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
    >
      <div
        style={{
          backgroundColor: "#FFFFFF",
          borderRadius: `${Math.round(22 * scale)}px`,
          padding: `${Math.round(32 * scale)}px`,
          width: `${Math.round(600 * scale)}px`,
          maxWidth: "90vw",
          maxHeight: "90vh",
          overflow: "auto",
          boxShadow: "0 4px 20px rgba(0, 0, 0, 0.15)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: `${Math.round(24 * scale)}px`,
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "flex-start",
              alignItems: "center",
              marginBottom: `${Math.round(24 * scale)}px`,
            }}
          >
            <img
              src={ASSETS.CHATBOT}
              style={{
                width: `${Math.round(32 * scale)}px`,
                height: `${Math.round(32 * scale)}px`,
                marginRight: `${Math.round(5 * scale)}px`,
              }}
            />
            <h2
              style={{
                fontSize: `${Math.round(24 * scale)}px`,
                fontWeight: 600,
                margin: 0,
                fontFamily: "Poppins, sans-serif",
              }}
            >
              AI Document Upload
            </h2>
          </div>
          <button
            onClick={handleClose}
            style={{
              background: "none",
              border: "none",
              fontSize: `${Math.round(24 * scale)}px`,
              cursor: "pointer",
              color: "#666",
            }}
          >
            ✕
          </button>
        </div>

        {!extractedData ? (
          <>
            {/* Upload Area */}
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              style={{
                border: `2px dashed ${dragActive ? "#4299e1" : "#cbd5e0"}`,
                borderRadius: `${Math.round(12 * scale)}px`,
                padding: `${Math.round(40 * scale)}px`,
                textAlign: "center",
                backgroundColor: dragActive ? "#ebf8ff" : "#f7fafc",
                transition: "all 0.3s",
                marginBottom: `${Math.round(20 * scale)}px`,
              }}
            >
              <div
                style={{
                  fontSize: `${Math.round(48 * scale)}px`,
                  marginBottom: `${Math.round(16 * scale)}px`,
                }}
              >
                📄
              </div>

              {file ? (
                <div>
                  <p
                    style={{
                      fontSize: `${Math.round(16 * scale)}px`,
                      fontWeight: 500,
                      color: "#2d3748",
                      marginBottom: `${Math.round(8 * scale)}px`,
                    }}
                  >
                    {file.name}
                  </p>
                  <p
                    style={{
                      fontSize: `${Math.round(14 * scale)}px`,
                      color: "#718096",
                    }}
                  >
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                  <button
                    onClick={() => setFile(null)}
                    style={{
                      marginTop: `${Math.round(12 * scale)}px`,
                      padding: `${Math.round(8 * scale)}px ${Math.round(
                        16 * scale
                      )}px`,
                      backgroundColor: "#f56565",
                      color: "white",
                      border: "none",
                      borderRadius: `${Math.round(6 * scale)}px`,
                      cursor: "pointer",
                      fontSize: `${Math.round(14 * scale)}px`,
                    }}
                  >
                    Remove
                  </button>
                </div>
              ) : (
                <>
                  <p
                    style={{
                      fontSize: `${Math.round(18 * scale)}px`,
                      fontWeight: 500,
                      color: "#2d3748",
                      marginBottom: `${Math.round(8 * scale)}px`,
                    }}
                  >
                    Drag and drop your CV here
                  </p>
                  <p
                    style={{
                      fontSize: `${Math.round(14 * scale)}px`,
                      color: "#718096",
                      marginBottom: `${Math.round(16 * scale)}px`,
                    }}
                  >
                    or
                  </p>
                  <label
                    style={{
                      display: "inline-block",
                      padding: `${Math.round(10 * scale)}px ${Math.round(
                        20 * scale
                      )}px`,
                      backgroundColor: "#4299e1",
                      color: "white",
                      borderRadius: `${Math.round(6 * scale)}px`,
                      cursor: "pointer",
                      fontSize: `${Math.round(14 * scale)}px`,
                      fontWeight: 500,
                    }}
                  >
                    Browse Files
                    <input
                      type="file"
                      onChange={handleFileChange}
                      accept=".pdf,.docx"
                      style={{ display: "none" }}
                    />
                  </label>
                  <p
                    style={{
                      fontSize: `${Math.round(12 * scale)}px`,
                      color: "#a0aec0",
                      marginTop: `${Math.round(16 * scale)}px`,
                    }}
                  >
                    Supported formats: PDF, DOCX (Max 10MB)
                  </p>
                </>
              )}
            </div>

            {/* Progress Bar */}
            {uploadProgress > 0 && uploadProgress < 100 && (
              <div
                style={{
                  marginBottom: `${Math.round(20 * scale)}px`,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: `${Math.round(8 * scale)}px`,
                  }}
                >
                  <span
                    style={{
                      fontSize: `${Math.round(14 * scale)}px`,
                      color: "#4a5568",
                    }}
                  >
                    Processing...
                  </span>
                  <span
                    style={{
                      fontSize: `${Math.round(14 * scale)}px`,
                      color: "#4a5568",
                      fontWeight: 500,
                    }}
                  >
                    {uploadProgress}%
                  </span>
                </div>
                <div
                  style={{
                    width: "100%",
                    height: `${Math.round(8 * scale)}px`,
                    backgroundColor: "#e2e8f0",
                    borderRadius: `${Math.round(4 * scale)}px`,
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      width: `${uploadProgress}%`,
                      height: "100%",
                      backgroundColor: "#48bb78",
                      transition: "width 0.3s",
                    }}
                  />
                </div>
              </div>
            )}

            {/* Info Box */}
            <div
              style={{
                backgroundColor: "#ebf8ff",
                border: "1px solid #bee3f8",
                borderRadius: `${Math.round(8 * scale)}px`,
                padding: `${Math.round(16 * scale)}px`,
                marginBottom: `${Math.round(24 * scale)}px`,
              }}
            >
              <p
                style={{
                  fontSize: `${Math.round(14 * scale)}px`,
                  color: "#2c5282",
                  margin: 0,
                  lineHeight: 1.6,
                }}
              >
                <strong>AI Processing:</strong> Our AI will automatically
                extract candidate information including name, email, phone,
                nationality, certificates, and experience from the uploaded
                document.
              </p>
            </div>

            {/* Actions */}
            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
                gap: `${Math.round(12 * scale)}px`,
              }}
            >
              <button
                onClick={handleClose}
                disabled={loading}
                style={{
                  padding: `${Math.round(10 * scale)}px ${Math.round(
                    20 * scale
                  )}px`,
                  backgroundColor: "#e2e8f0",
                  color: "#4a5568",
                  border: "none",
                  borderRadius: `${Math.round(6 * scale)}px`,
                  cursor: loading ? "not-allowed" : "pointer",
                  fontSize: `${Math.round(14 * scale)}px`,
                  fontWeight: 500,
                  opacity: loading ? 0.5 : 1,
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleUpload}
                disabled={!file || loading}
                style={{
                  padding: `${Math.round(10 * scale)}px ${Math.round(
                    20 * scale
                  )}px`,
                  backgroundColor: file && !loading ? "#48bb78" : "#cbd5e0",
                  color: "white",
                  border: "none",
                  borderRadius: `${Math.round(6 * scale)}px`,
                  cursor: file && !loading ? "pointer" : "not-allowed",
                  fontSize: `${Math.round(14 * scale)}px`,
                  fontWeight: 500,
                }}
              >
                {loading ? "Processing..." : "Upload & Process"}
              </button>
            </div>
          </>
        ) : (
          // Success State
          <div style={{ textAlign: "center" }}>
            <div
              style={{
                fontSize: `${Math.round(64 * scale)}px`,
                marginBottom: `${Math.round(16 * scale)}px`,
              }}
            >
              ✅
            </div>
            <h3
              style={{
                fontSize: `${Math.round(20 * scale)}px`,
                fontWeight: 600,
                color: "#2d3748",
                marginBottom: `${Math.round(8 * scale)}px`,
              }}
            >
              Document Processed Successfully!
            </h3>
            <p
              style={{
                fontSize: `${Math.round(14 * scale)}px`,
                color: "#718096",
                marginBottom: `${Math.round(24 * scale)}px`,
              }}
            >
              Extracted data from: {file?.name}
            </p>

            {/* Extracted Data Preview */}
            <div
              style={{
                backgroundColor: "#f7fafc",
                borderRadius: `${Math.round(8 * scale)}px`,
                padding: `${Math.round(16 * scale)}px`,
                textAlign: "left",
                marginBottom: `${Math.round(20 * scale)}px`,
              }}
            >
              <h4
                style={{
                  fontSize: `${Math.round(16 * scale)}px`,
                  fontWeight: 600,
                  marginBottom: `${Math.round(12 * scale)}px`,
                }}
              >
                Extracted Information:
              </h4>
              {Object.entries(extractedData || {}).map(([key, value]) => (
                <div
                  key={key}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    padding: `${Math.round(6 * scale)}px 0`,
                    borderBottom: "1px solid #e2e8f0",
                  }}
                >
                  <span
                    style={{
                      fontSize: `${Math.round(14 * scale)}px`,
                      color: "#4a5568",
                      textTransform: "capitalize",
                    }}
                  >
                    {key.replace(/_/g, " ")}:
                  </span>
                  <span
                    style={{
                      fontSize: `${Math.round(14 * scale)}px`,
                      color: "#2d3748",
                      fontWeight: 500,
                    }}
                  >
                    {Array.isArray(value) ? value.join(", ") : value || "N/A"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentUploadModal;
