/* eslint-disable no-unused-vars */
import React, { useState } from "react";
import ChatWidget from "../Components/AI/ChatWidget";
import aiApi from "../../../services/Dashboard/aiApi";
import { ASSETS } from "../../../utils/constants";

const AIApplication = ({ scale = 1, isMobile = false }) => {
  const [activeTab, setActiveTab] = useState("chat");
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        setUploadFile(file);
      }
    }
  };

  const validateFile = (file) => {
    const validTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];
    const maxSize = 10 * 1024 * 1024;

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

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (validateFile(file)) {
        setUploadFile(file);
      }
    }
  };

  const handleUpload = async () => {
    if (!uploadFile) return;

    setUploading(true);
    const result = await aiApi.uploadDocument(uploadFile);

    if (result.success) {
      setUploadResult(result.data);
      setTimeout(() => {
        setUploadFile(null);
        setUploadResult(null);
      }, 5000);
    }

    setUploading(false);
  };

  const headerHeight = Math.round(101 * scale);

  return (
    <main
      style={{
        padding: `${Math.round(12 * scale)}px`,
        marginTop: `calc(${headerHeight}px + ${Math.round(12 * scale)}px)`,
        overflow: "auto",
        flex: 1,
        backgroundColor: "#f7fafc",
      }}
    >
      {/* Header */}
      <div
        style={{
          marginBottom: `${Math.round(32 * scale)}px`,
          textAlign: "center",
        }}
      >
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            gap: `${Math.round(16 * scale)}px`,
            marginBottom: `${Math.round(16 * scale)}px`,
          }}
        >
          <img
            src={ASSETS.AI_ICON || ASSETS.LOGO}
            alt="AI"
            style={{
              width: `${Math.round(60 * scale)}px`,
              height: `${Math.round(60 * scale)}px`,
              objectFit: "contain",
            }}
          />
          <h1
            style={{
              fontSize: `${Math.round(36 * scale)}px`,
              fontWeight: 700,
              margin: 0,
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            AI Assistant
          </h1>
        </div>
        <p
          style={{
            fontSize: `${Math.round(16 * scale)}px`,
            color: "#718096",
            margin: 0,
          }}
        >
          Chat with AI or upload documents for processing
        </p>
      </div>

      {/* Tabs */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: `${Math.round(16 * scale)}px`,
          marginBottom: `${Math.round(32 * scale)}px`,
        }}
      >
        {[
          { id: "chat", label: "💬 AI Chat", icon: "💬" },
          { id: "upload", label: "📄 Upload Document", icon: "📄" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: `${Math.round(14 * scale)}px ${Math.round(
                32 * scale
              )}px`,
              backgroundColor: activeTab === tab.id ? "#667eea" : "white",
              color: activeTab === tab.id ? "white" : "#4a5568",
              border: activeTab === tab.id ? "none" : "2px solid #e2e8f0",
              borderRadius: `${Math.round(12 * scale)}px`,
              fontSize: `${Math.round(16 * scale)}px`,
              fontWeight: 600,
              cursor: "pointer",
              transition: "all 0.3s",
              boxShadow:
                activeTab === tab.id
                  ? "0 4px 12px rgba(102, 126, 234, 0.3)"
                  : "none",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div
        style={{
          maxWidth: `${Math.round(1200 * scale)}px`,
          margin: "0 auto",
        }}
      >
        {activeTab === "chat" ? (
          <div
            style={{
              height: `${Math.round(700 * scale)}px`,
              display: "flex",
              justifyContent: "center",
              borderRadius: "20px",
            }}
          >
            <ChatWidget scale={scale} isFloating={false} />
          </div>
        ) : (
          <div
            style={{
              backgroundColor: "white",
              borderRadius: `${Math.round(20 * scale)}px`,
              padding: `${Math.round(40 * scale)}px`,
              boxShadow: "0 4px 20px rgba(0, 0, 0, 0.08)",
            }}
          >
            {/* Upload Area */}
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              style={{
                border: `3px dashed ${dragActive ? "#667eea" : "#cbd5e0"}`,
                borderRadius: `${Math.round(16 * scale)}px`,
                padding: `${Math.round(60 * scale)}px`,
                textAlign: "center",
                backgroundColor: dragActive ? "#ebf8ff" : "#f7fafc",
                transition: "all 0.3s",
                marginBottom: `${Math.round(32 * scale)}px`,
              }}
            >
              <div
                style={{
                  fontSize: `${Math.round(64 * scale)}px`,
                  marginBottom: `${Math.round(20 * scale)}px`,
                }}
              >
                📄
              </div>

              {uploadFile ? (
                <div>
                  <p
                    style={{
                      fontSize: `${Math.round(18 * scale)}px`,
                      fontWeight: 600,
                      color: "#2d3748",
                      marginBottom: `${Math.round(8 * scale)}px`,
                    }}
                  >
                    {uploadFile.name}
                  </p>
                  <p
                    style={{
                      fontSize: `${Math.round(14 * scale)}px`,
                      color: "#718096",
                      marginBottom: `${Math.round(16 * scale)}px`,
                    }}
                  >
                    {(uploadFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                  <div
                    style={{
                      display: "flex",
                      gap: `${Math.round(12 * scale)}px`,
                      justifyContent: "center",
                    }}
                  >
                    <button
                      onClick={() => setUploadFile(null)}
                      style={{
                        padding: `${Math.round(10 * scale)}px ${Math.round(
                          24 * scale
                        )}px`,
                        backgroundColor: "#f56565",
                        color: "white",
                        border: "none",
                        borderRadius: `${Math.round(8 * scale)}px`,
                        cursor: "pointer",
                        fontSize: `${Math.round(14 * scale)}px`,
                        fontWeight: 500,
                      }}
                    >
                      Remove
                    </button>
                    <button
                      onClick={handleUpload}
                      disabled={uploading}
                      style={{
                        padding: `${Math.round(10 * scale)}px ${Math.round(
                          24 * scale
                        )}px`,
                        backgroundColor: uploading ? "#cbd5e0" : "#48bb78",
                        color: "white",
                        border: "none",
                        borderRadius: `${Math.round(8 * scale)}px`,
                        cursor: uploading ? "not-allowed" : "pointer",
                        fontSize: `${Math.round(14 * scale)}px`,
                        fontWeight: 500,
                      }}
                    >
                      {uploading ? "Processing..." : "Upload & Process"}
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <p
                    style={{
                      fontSize: `${Math.round(20 * scale)}px`,
                      fontWeight: 600,
                      color: "#2d3748",
                      marginBottom: `${Math.round(12 * scale)}px`,
                    }}
                  >
                    Drag and drop your CV here
                  </p>
                  <p
                    style={{
                      fontSize: `${Math.round(14 * scale)}px`,
                      color: "#718096",
                      marginBottom: `${Math.round(20 * scale)}px`,
                    }}
                  >
                    or
                  </p>
                  <label
                    style={{
                      display: "inline-block",
                      padding: `${Math.round(14 * scale)}px ${Math.round(
                        32 * scale
                      )}px`,
                      background:
                        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                      color: "white",
                      borderRadius: `${Math.round(10 * scale)}px`,
                      cursor: "pointer",
                      fontSize: `${Math.round(16 * scale)}px`,
                      fontWeight: 600,
                      boxShadow: "0 4px 12px rgba(102, 126, 234, 0.3)",
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
                      marginTop: `${Math.round(20 * scale)}px`,
                    }}
                  >
                    Supported formats: PDF, DOCX (Max 10MB)
                  </p>
                </>
              )}
            </div>

            {/* Upload Success */}
            {uploadResult && (
              <div
                style={{
                  backgroundColor: "#f0fff4",
                  border: "2px solid #9ae6b4",
                  borderRadius: `${Math.round(12 * scale)}px`,
                  padding: `${Math.round(24 * scale)}px`,
                  textAlign: "center",
                }}
              >
                <div
                  style={{
                    fontSize: `${Math.round(48 * scale)}px`,
                    marginBottom: `${Math.round(12 * scale)}px`,
                  }}
                >
                  ✅
                </div>
                <h3
                  style={{
                    fontSize: `${Math.round(20 * scale)}px`,
                    fontWeight: 600,
                    color: "#22543d",
                    marginBottom: `${Math.round(8 * scale)}px`,
                  }}
                >
                  Document Processed Successfully!
                </h3>
                <p
                  style={{
                    fontSize: `${Math.round(14 * scale)}px`,
                    color: "#2f855a",
                  }}
                >
                  Your document has been analyzed and processed by AI
                </p>
              </div>
            )}

            {/* Info Box */}
            <div
              style={{
                backgroundColor: "#ebf8ff",
                border: "1px solid #bee3f8",
                borderRadius: `${Math.round(12 * scale)}px`,
                padding: `${Math.round(24 * scale)}px`,
                marginTop: `${Math.round(24 * scale)}px`,
              }}
            >
              <h4
                style={{
                  fontSize: `${Math.round(16 * scale)}px`,
                  fontWeight: 600,
                  color: "#2c5282",
                  marginBottom: `${Math.round(12 * scale)}px`,
                  display: "flex",
                  alignItems: "center",
                  gap: `${Math.round(8 * scale)}px`,
                }}
              >
                <img
                  src={ASSETS.AI_ICON || ASSETS.LOGO}
                  alt="AI"
                  style={{
                    width: `${Math.round(24 * scale)}px`,
                    height: `${Math.round(24 * scale)}px`,
                  }}
                />
                AI Document Processing
              </h4>
              <p
                style={{
                  fontSize: `${Math.round(14 * scale)}px`,
                  color: "#2c5282",
                  margin: 0,
                  lineHeight: 1.6,
                }}
              >
                Our AI automatically extracts candidate information including
                name, email, phone, nationality, certificates, experience, and
                ranks from uploaded documents. The processed data is instantly
                available in the system.
              </p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
};

export default AIApplication;
