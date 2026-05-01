import React, { useState, useRef, useEffect } from "react";
import defaultAiApi from "../../../../services/Dashboard/aiApi";
import { ASSETS as DEFAULT_ASSETS } from "../../../../utils/constants";
import { Trash2, Minimize2, Send, Sparkles, Copy, Check } from "lucide-react";

const ChatWidget = ({
  scale = 1,
  isFloating = true,
  aiApi: aiApiProp,
  ASSETS: ASSETSprop,
}) => {
  const aiApi = aiApiProp || defaultAiApi;
  const ASSETS = ASSETSprop || DEFAULT_ASSETS;

  const [isOpen, setIsOpen] = useState(!isFloating);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [currentSession, setCurrentSession] = useState(null);
  const [error, setError] = useState(null);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          role: "assistant",
          content:
            "👋 Hello! I'm your AI assistant. I can help you with:\n\n• Finding seafarers by rank or certificate\n• Getting statistics and reports\n• Ship and crew information\n• Interview scheduling\n• Company details\n\nWhat would you like to know?",
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  }, [isOpen]);

  const handleSend = async () => {
    if (!inputMessage.trim() || isTyping) return;

    const userMessage = {
      role: "user",
      content: inputMessage.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsTyping(true);
    setError(null);

    try {
      const result = await aiApi.sendChatMessage(
        userMessage.content,
        currentSession
      );

      if (result.success) {
        setCurrentSession(result.data.session_id);
        const assistantMessage = {
          role: "assistant",
          content: result.data.response,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        setError(result.error || "Failed to send message");
      }
    } catch (err) {
      setError("An error occurred. Please try again.");
      console.error(err);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleQuickAction = (query) => {
    setInputMessage(query);
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  const handleClearChat = () => {
    if (window.confirm("Clear all messages?")) {
      setMessages([]);
      setCurrentSession(null);
      setError(null);
    }
  };

  const handleCopyMessage = (content, index) => {
    navigator.clipboard.writeText(content);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Floating widget button
  if (isFloating && !isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="chat-widget-fab"
        style={{
          width: `${Math.round(60 * scale)}`,
          height: `${Math.round(60 * scale)}`,
          position: "fixed",
          bottom: `${Math.round(30 * scale)}px`,
          right: `${Math.round(30 * scale)}px`,
          borderRadius: `${Math.round(20 * scale)}px`,
          color: "white",
          border: "none",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 998,
          transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
          overflow: "hidden",
        }}
      >
        <img
          src={ASSETS.CHATBOT}
          style={{
            width: `${Math.round(60 * scale)}`,
            height: `${Math.round(60 * scale)}`,
          }}
        />
        <style>{`.chat-widget-fab:hover { transform: scale(1.08) rotate(4deg); }.chat-widget-fab:active { transform: scale(0.96); }`}</style>
      </button>
    );
  }

  const chatContainerStyle = isFloating
    ? {
        position: "fixed",
        bottom: `${Math.round(30 * scale)}px`,
        right: `${Math.round(30 * scale)}px`,
        width: `${Math.round(400 * scale)}px`,
        height: `${Math.round(500 * scale)}px`,
        zIndex: 999,
      }
    : {
        width: "100%",
        height: `${Math.round(700 * scale)}px`,
        maxWidth: `${Math.round(1000 * scale)}px`,
        margin: "0 auto",
      };

  const quickActions = [
    "Find all seafarers with Master rank",
    "Show upcoming interviews this week",
    "List all active companies",
    "Get statistics for this month",
  ];

  return (
    <div style={chatContainerStyle}>
      <div
        className="chat-container"
        style={{
          backgroundColor: "#ffffff",
          borderRadius: `${Math.round(24 * scale)}px`,
          boxShadow: isFloating
            ? "0 20px 60px rgba(0, 0, 0, 0.12), 0 0 1px rgba(0, 0, 0, 0.04)"
            : "0 4px 20px rgba(0, 0, 0, 0.06)",
          display: "flex",
          flexDirection: "column",
          height: "100%",
          overflow: "hidden",
          border: "1px solid rgba(0, 101, 175, 0.06)",
        }}
      >
        {/* Header */}
        <div
          className="chat-header"
          style={{
            background: "linear-gradient(135deg, #0065AF 0%, #25548E 100%)",
            color: "white",
            padding: `${Math.round(18 * scale)}px ${Math.round(20 * scale)}px`,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            borderTopLeftRadius: `${Math.round(24 * scale)}px`,
            borderTopRightRadius: `${Math.round(24 * scale)}px`,
            boxShadow: "0 4px 12px rgba(0, 101, 175, 0.12)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: `${Math.round(14 * scale)}px`,
            }}
          >
            <div
              style={{
                width: `${Math.round(48 * scale)}px`,
                height: `${Math.round(48 * scale)}px`,
                borderRadius: "50%",
                background: "rgba(255,255,255,0.16)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                border: "2px solid rgba(255,255,255,0.16)",
              }}
            >
              <img
                src={ASSETS.CHATBOT || ASSETS.LOGO}
                alt="AI"
                style={{ width: "70%", height: "70%", objectFit: "contain" }}
              />
            </div>
            <div>
              <h3
                style={{
                  margin: 0,
                  fontSize: `${Math.round(18 * scale)}px`,
                  fontWeight: 600,
                }}
              >
                AI Assistant
              </h3>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: `${Math.round(6 * scale)}px`,
                  marginTop: `${Math.round(4 * scale)}px`,
                }}
              >
                <div
                  className="pulse-dot"
                  style={{
                    width: `${Math.round(8 * scale)}px`,
                    height: `${Math.round(8 * scale)}px`,
                    borderRadius: "50%",
                    backgroundColor: isTyping ? "#FCD34D" : "#10B981",
                  }}
                />
                <p
                  style={{
                    margin: 0,
                    fontSize: `${Math.round(13 * scale)}px`,
                    opacity: 0.95,
                    fontWeight: 500,
                  }}
                >
                  {isTyping ? "Typing..." : "Online"}
                </p>
              </div>
            </div>
          </div>

          <div style={{ display: "flex", gap: `${Math.round(8 * scale)}px` }}>
            <button
              onClick={handleClearChat}
              className="header-btn"
              title="Clear Chat"
              style={{
                background: "rgba(255,255,255,0.12)",
                border: "1px solid rgba(255,255,255,0.12)",
                color: "white",
                borderRadius: `${Math.round(10 * scale)}px`,
                width: `${Math.round(36 * scale)}px`,
                height: `${Math.round(36 * scale)}px`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Trash2 size={Math.round(18 * scale)} strokeWidth={2} />
            </button>
            {isFloating && (
              <button
                onClick={() => setIsOpen(false)}
                className="header-btn"
                title="Minimize"
                style={{
                  background: "rgba(255,255,255,0.12)",
                  border: "1px solid rgba(255,255,255,0.12)",
                  color: "white",
                  borderRadius: `${Math.round(10 * scale)}px`,
                  width: `${Math.round(36 * scale)}px`,
                  height: `${Math.round(36 * scale)}px`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Minimize2 size={Math.round(18 * scale)} strokeWidth={2} />
              </button>
            )}
          </div>
        </div>

        {/* Messages Area */}
        <div
          className="messages-container"
          style={{
            flex: 1,
            overflowY: "auto",
            padding: `${Math.round(22 * scale)}px`,
            background: "linear-gradient(180deg,#F9FAFB 0%,#F3F4F6 100%)",
            display: "flex",
            flexDirection: "column",
            gap: `${Math.round(14 * scale)}px`,
          }}
        >
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className="message-wrapper"
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: msg.role === "user" ? "flex-end" : "flex-start",
                animation: "slideIn 0.28s ease-out",
              }}
            >
              <div
                className="message-bubble"
                style={{
                  maxWidth: "85%",
                  padding: `${Math.round(12 * scale)}px ${Math.round(
                    16 * scale
                  )}px`,
                  borderRadius: `${Math.round(14 * scale)}px`,
                  background:
                    msg.role === "user"
                      ? "linear-gradient(135deg,#0065AF 0%,#25548E 100%)"
                      : "white",
                  color: msg.role === "user" ? "white" : "#111827",
                  fontSize: `${Math.round(14 * scale)}px`,
                  lineHeight: 1.6,
                  boxShadow:
                    msg.role === "user"
                      ? "0 6px 18px rgba(0,101,175,0.18)"
                      : "0 2px 8px rgba(0,0,0,0.06)",
                  position: "relative",
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-word",
                  border:
                    msg.role === "assistant"
                      ? "1px solid rgba(0,0,0,0.06)"
                      : "none",
                }}
              >
                {msg.content}
                {msg.role === "assistant" && (
                  <button
                    onClick={() => handleCopyMessage(msg.content, idx)}
                    className="copy-btn"
                    title="Copy"
                    style={{
                      position: "absolute",
                      top: `${Math.round(8 * scale)}px`,
                      right: `${Math.round(8 * scale)}px`,
                      background: "rgba(0,0,0,0.04)",
                      border: "1px solid rgba(0,0,0,0.08)",
                      borderRadius: `${Math.round(6 * scale)}px`,
                      padding: `${Math.round(4 * scale)}px ${Math.round(
                        8 * scale
                      )}px`,
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      gap: `${Math.round(6 * scale)}px`,
                      fontSize: `${Math.round(11 * scale)}px`,
                      color: "#6B7280",
                    }}
                  >
                    {copiedIndex === idx ? (
                      <>
                        <Check size={Math.round(12 * scale)} />{" "}
                        <span>Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy size={Math.round(12 * scale)} /> <span>Copy</span>
                      </>
                    )}
                  </button>
                )}
              </div>
              <div
                style={{
                  fontSize: `${Math.round(11 * scale)}px`,
                  color: "#9CA3AF",
                  marginTop: `${Math.round(6 * scale)}px`,
                  padding: `0 ${Math.round(4 * scale)}px`,
                  fontWeight: 500,
                }}
              >
                {formatTimestamp(msg.timestamp)}
              </div>
            </div>
          ))}

          {/* Typing indicator */}
          {isTyping && (
            <div
              className="typing-indicator"
              style={{
                display: "flex",
                alignItems: "center",
                gap: `${Math.round(8 * scale)}px`,
              }}
            >
              <div
                style={{
                  padding: `${Math.round(12 * scale)}px ${Math.round(
                    16 * scale
                  )}px`,
                  borderRadius: `${Math.round(12 * scale)}px`,
                  background: "white",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
                  border: "1px solid rgba(0,0,0,0.06)",
                  display: "flex",
                  gap: `${Math.round(8 * scale)}px`,
                }}
              >
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="typing-dot"
                    style={{
                      width: `${Math.round(8 * scale)}px`,
                      height: `${Math.round(8 * scale)}px`,
                      borderRadius: "50%",
                      backgroundColor: "#0065AF",
                      opacity: 0.7,
                      animationDelay: `${i * 0.14}s`,
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          {error && (
            <div
              style={{
                backgroundColor: "#FEF2F2",
                border: "1px solid #FCA5A5",
                borderRadius: `${Math.round(12 * scale)}px`,
                padding: `${Math.round(12 * scale)}px`,
                color: "#B91C1C",
              }}
            >
              {error}
            </div>
          )}

          {/* Quick actions */}
          {messages.length <= 1 && !isTyping && (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: `${Math.round(10 * scale)}px`,
                marginTop: `${Math.round(8 * scale)}px`,
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: `${Math.round(8 * scale)}px`,
                  fontSize: `${Math.round(12 * scale)}px`,
                  color: "#6B7280",
                  fontWeight: 600,
                  textTransform: "uppercase",
                  letterSpacing: "0.04em",
                }}
              >
                <Sparkles size={Math.round(14 * scale)} /> Try asking:
              </div>
              {quickActions.map((action, idx) => (
                <button
                  key={idx}
                  onClick={() => handleQuickAction(action)}
                  className="quick-action-btn"
                  style={{
                    backgroundColor: "white",
                    border: "1px solid #E5E7EB",
                    borderRadius: `${Math.round(12 * scale)}px`,
                    padding: `${Math.round(12 * scale)}px ${Math.round(
                      16 * scale
                    )}px`,
                    fontSize: `${Math.round(13 * scale)}px`,
                    color: "#374151",
                    cursor: "pointer",
                    textAlign: "left",
                    transition: "all 0.18s",
                    fontWeight: 500,
                  }}
                >
                  {action}
                </button>
              ))}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div
          style={{
            padding: `${Math.round(18 * scale)}px ${Math.round(20 * scale)}px`,
            backgroundColor: "white",
            borderTop: "1px solid #E5E7EB",
            boxShadow: "0 -4px 12px rgba(0,0,0,0.04)",
          }}
        >
          <div
            style={{
              display: "flex",
              gap: `${Math.round(12 * scale)}px`,
              alignItems: "center",
            }}
          >
            <div style={{ flex: 1, position: "relative" }}>
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                disabled={isTyping}
                style={{
                  width: "100%",
                  padding: `${Math.round(12 * scale)}px ${Math.round(
                    14 * scale
                  )}px`,
                  border: "2px solid #E5E7EB",
                  borderRadius: `${Math.round(12 * scale)}px`,
                  fontSize: `${Math.round(14 * scale)}px`,
                  resize: "none",
                  minHeight: `${Math.round(52 * scale)}px`,
                  maxHeight: `${Math.round(120 * scale)}px`,
                  backgroundColor: "#F9FAFB",
                }}
                rows={1}
                onInput={(e) => {
                  e.target.style.height = "auto";
                  e.target.style.height =
                    Math.min(e.target.scrollHeight, 120 * scale) + "px";
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = "#0065AF";
                  e.target.style.backgroundColor = "white";
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = "#E5E7EB";
                  e.target.style.backgroundColor = "#F9FAFB";
                }}
              />
            </div>
            <button
              onClick={handleSend}
              disabled={!inputMessage.trim() || isTyping}
              className="send-btn"
              style={{
                background:
                  inputMessage.trim() && !isTyping
                    ? "linear-gradient(135deg,#0065AF 0%,#25548E 100%)"
                    : "#E5E7EB",
                color: "white",
                border: "none",
                borderRadius: `${Math.round(12 * scale)}px`,
                padding: `${Math.round(12 * scale)}px ${Math.round(
                  18 * scale
                )}px`,
                cursor:
                  inputMessage.trim() && !isTyping ? "pointer" : "not-allowed",
                fontSize: `${Math.round(14 * scale)}px`,
                fontWeight: 600,
                minWidth: `${Math.round(52 * scale)}px`,
                height: `${Math.round(44 * scale)}px`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: `${Math.round(8 * scale)}px`,
              }}
            >
              <Send size={Math.round(18 * scale)} strokeWidth={2.5} />
            </button>
          </div>
        </div>
      </div>

      <style>{`\n        @keyframes slideIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }\n        @keyframes bounce { 0%,80%,100%{ transform: scale(0);} 40%{ transform: scale(1);} }\n        .message-wrapper { animation: slideIn 0.28s cubic-bezier(0.4,0,0.2,1); }\n        .pulse-dot { animation: pulse 2s cubic-bezier(0.4,0,0.6,1) infinite; }\n        .typing-dot { animation: bounce 1.4s infinite ease-in-out; }\n        .header-btn:hover { transform: scale(1.06); }\n        .copy-btn:hover { background: rgba(0,0,0,0.08) !important; border-color: rgba(0,0,0,0.12) !important; }\n        .quick-action-btn:hover { background: #F9FAFB !important; border-color: #0065AF !important; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,101,175,0.12); }\n        .send-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(0,101,175,0.18) !important; }\n        .messages-container::-webkit-scrollbar { width: 6px; }\n        .messages-container::-webkit-scrollbar-track { background: transparent; }\n        .messages-container::-webkit-scrollbar-thumb { background: rgba(0,101,175,0.18); border-radius: 3px; }\n        .messages-container::-webkit-scrollbar-thumb:hover { background: rgba(0,101,175,0.36); }\n      `}</style>
    </div>
  );
};

export default ChatWidget;
