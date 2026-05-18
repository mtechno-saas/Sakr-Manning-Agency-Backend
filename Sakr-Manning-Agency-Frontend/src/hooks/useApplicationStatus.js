import { useState, useEffect, useCallback } from "react";
import { cvSubmissionsApi } from "../services/Dashboard/cvSubmissionsApi";
import { tokenStorage } from "../services/Auth/tokenStorage";

/**
 * Derives the user's application status from their CV submission documents.
 *
 * Statuses:
 *  "none"        — no documents found → redirect to /quick-apply
 *  "pending"     — documents exist but none are Active → pending approval
 *  "active"      — at least one Active document → form access allowed
 *  "blacklisted" — only Blacklist documents → access denied
 *
 * @returns {{ status: string, isLoading: boolean, error: string|null, refetch: () => void }}
 */
export function useApplicationStatus() {
    const [status, setStatus] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchStatus = useCallback(async () => {
        // If not logged in, return early without calling the backend
        const token = tokenStorage.getAccessToken();
        if (!token) {
            setStatus(null);
            setIsLoading(false);
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const data = await cvSubmissionsApi.getDocuments();

            // The API may return a paginated response ({ results: [...] }) or a plain array
            const documents = Array.isArray(data) ? data : data?.results ?? [];

            // Filter documents to include only those belonging to the logged-in user by ID
            const user = tokenStorage.getUser();
            const userDocs = documents.filter((doc) => {
                const docUserId = doc.user;
                return String(docUserId) === String(user?.id);
            });

            if (userDocs.length === 0) {
                setStatus("none");
                return;
            }

            const hasActive = userDocs.some(
                (doc) => doc.status?.toLowerCase() === "active"
            );
            if (hasActive) {
                setStatus("Active");
                return;
            }

            const allBlacklisted = userDocs.every(
                (doc) => doc.status?.toLowerCase() === "blacklist"
            );
            if (allBlacklisted) {
                setStatus("Blacklist");
                return;
            }

            // Mix of Pending / other non-active statuses
            setStatus("Pending");
        } catch (err) {
            console.error("useApplicationStatus error:", err);
            setError(err.message || "Failed to check application status");
            setStatus(null);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchStatus();
    }, [fetchStatus]);

    return { status, isLoading, error, refetch: fetchStatus };
}
