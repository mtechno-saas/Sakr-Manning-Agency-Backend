// hooks/dashboard/useAI.js
import { useState, useCallback } from "react";
import aiApi from "../../services/Dashboard/aiApi";
import useNotification from "../../components/dashboard/hooks/useNotification";

/**
 * Custom hook for AI features
 * Handles document processing and chat functionality
 */
const useAI = () => {
  const { notify } = useNotification();
  const [loading, setLoading] = useState(false);
  // const [applicants, setApplicants] = useState([]);
  const [chatSessions, setChatSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);

  // ============================================
  // DOCUMENT PROCESSING
  // ============================================

  /**
   * Upload and process document
   */
  const uploadDocument = useCallback(
    async (file) => {
      setLoading(true);
      try {
        const result = await aiApi.uploadDocument(file);

        if (result.success) {
          notify.success("Document processed successfully!");

          // Refresh applicants list
          // await fetchApplicants();

          return result.data;
        } else {
          notify.error(result.error || "Failed to process document");
          return null;
        }
      } catch (error) {
        notify.error("An error occurred while processing document");
        console.error(error);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [notify]
  );

  /**
   * Fetch all applicants
   */
  // const fetchApplicants = useCallback(async () => {
  //   setLoading(true);
  //   try {
  //     const result = await aiApi.getApplicants();

  //     if (result.success) {
  //       setApplicants(result.data);
  //     } else {
  //       notify.error(result.error || "Failed to fetch applicants");
  //     }
  //   } catch (error) {
  //     notify.error("An error occurred while fetching applicants");
  //     console.error(error);
  //   } finally {
  //     setLoading(false);
  //   }
  // }, [notify]);

  // /**
  //  * Get applicant by ID
  //  */
  // const getApplicantById = useCallback(
  //   async (applicantId) => {
  //     setLoading(true);
  //     try {
  //       const result = await aiApi.getApplicantById(applicantId);

  //       if (result.success) {
  //         return result.data;
  //       } else {
  //         notify.error(result.error || "Failed to fetch applicant");
  //         return null;
  //       }
  //     } catch (error) {
  //       notify.error("An error occurred while fetching applicant");
  //       console.error(error);
  //       return null;
  //     } finally {
  //       setLoading(false);
  //     }
  //   },
  //   [notify]
  // );

  // /**
  //  * Convert applicant to user
  //  */
  // const convertToUser = useCallback(
  //   async (applicantId, userData) => {
  //     setLoading(true);
  //     try {
  //       const result = await aiApi.convertApplicantToUser(
  //         applicantId,
  //         userData
  //       );

  //       if (result.success) {
  //         notify.success("Applicant converted to user successfully!");

  //         // Refresh applicants list
  //         await fetchApplicants();

  //         return result.data;
  //       } else {
  //         notify.error(result.error || "Failed to convert applicant");
  //         return null;
  //       }
  //     } catch (error) {
  //       notify.error("An error occurred while converting applicant");
  //       console.error(error);
  //       return null;
  //     } finally {
  //       setLoading(false);
  //     }
  //   },
  //   [notify, fetchApplicants]
  // );

  // /**
  //  * Batch convert applicants
  //  */
  // const batchConvert = useCallback(
  //   async (conversions) => {
  //     setLoading(true);
  //     try {
  //       const result = await aiApi.batchConvertApplicants(conversions);

  //       if (result.success) {
  //         notify.success(
  //           `Successfully converted ${conversions.length} applicants!`
  //         );

  //         // Refresh applicants list
  //         await fetchApplicants();

  //         return result.data;
  //       } else {
  //         notify.error(result.error || "Failed to batch convert applicants");
  //         return null;
  //       }
  //     } catch (error) {
  //       notify.error("An error occurred during batch conversion");
  //       console.error(error);
  //       return null;
  //     } finally {
  //       setLoading(false);
  //     }
  //   },
  //   [notify, fetchApplicants]
  // );

  // /**
  //  * Get sync status
  //  */
  // const getSyncStatus = useCallback(async () => {
  //   try {
  //     const result = await aiApi.getSyncStatus();
  //     return result.success ? result.data : null;
  //   } catch (error) {
  //     console.error("Failed to get sync status:", error);
  //     return null;
  //   }
  // }, []);

  // ============================================
  // CHAT FUNCTIONALITY
  // ============================================

  /**
   * Send message to AI
   */
  const sendMessage = useCallback(
    async (message, sessionId = null) => {
      setLoading(true);
      try {
        const result = await aiApi.sendChatMessage(message, sessionId);

        if (result.success) {
          // Update current session
          setCurrentSession(result.data.session_id);

          // Add message to history
          setChatHistory((prev) => [
            ...prev,
            {
              role: "user",
              content: message,
              timestamp: new Date().toISOString(),
            },
            {
              role: "assistant",
              content: result.data.response,
              timestamp: new Date().toISOString(),
            },
          ]);

          return result.data;
        } else {
          notify.error(result.error || "Failed to send message");
          return null;
        }
      } catch (error) {
        notify.error("An error occurred while sending message");
        console.error(error);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [notify]
  );

  /**
   * Load chat history
   */
  const loadChatHistory = useCallback(
    async (sessionId) => {
      setLoading(true);
      try {
        const result = await aiApi.getChatHistory(sessionId);

        if (result.success) {
          setChatHistory(result.data);
          setCurrentSession(sessionId);
        } else {
          notify.error(result.error || "Failed to load chat history");
        }
      } catch (error) {
        notify.error("An error occurred while loading chat history");
        console.error(error);
      } finally {
        setLoading(false);
      }
    },
    [notify]
  );

  /**
   * Fetch chat sessions
   */
  const fetchChatSessions = useCallback(async () => {
    try {
      const result = await aiApi.getChatSessions();

      if (result.success) {
        setChatSessions(result.data);
      }
    } catch (error) {
      console.error("Failed to fetch chat sessions:", error);
    }
  }, []);

  /**
   * Start new chat session
   */
  const startNewChat = useCallback(() => {
    setCurrentSession(null);
    setChatHistory([]);
  }, []);

  /**
   * Get AI capabilities
   */
  const getCapabilities = useCallback(async () => {
    try {
      const result = await aiApi.getCapabilities();
      return result.success ? result.data : null;
    } catch (error) {
      console.error("Failed to get AI capabilities:", error);
      return null;
    }
  }, []);

  return {
    // State
    loading,
    // applicants,
    chatSessions,
    currentSession,
    chatHistory,

    // Document Processing
    uploadDocument,
    // fetchApplicants,
    // getApplicantById,
    // convertToUser,
    // batchConvert,
    // getSyncStatus,

    // Chat
    sendMessage,
    loadChatHistory,
    fetchChatSessions,
    startNewChat,
    getCapabilities,
  };
};

export default useAI;
