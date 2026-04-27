// hooks/useSaveLock.js
import { useState, useCallback, useRef } from "react";

/**
 * Hook to manage save state locking
 * Prevents concurrent save operations that could cause data corruption
 */
export const useSaveLock = () => {
    const [isLocked, setIsLocked] = useState(false);
    const [lockReason, setLockReason] = useState(null);
    const lockTimeoutRef = useRef(null);

    /**
     * Acquire the save lock
     * @param {string} reason - Reason for locking (for debugging)
     * @param {number} maxDuration - Maximum lock duration in ms (default: 30s)
     * @returns {boolean} True if lock acquired, false if already locked
     */
    const acquireLock = useCallback((reason = "save", maxDuration = 30000) => {
        if (isLocked) {
            console.warn(`Save locked: ${lockReason}. Cannot acquire for: ${reason}`);
            return false;
        }

        setIsLocked(true);
        setLockReason(reason);

        // Safety timeout - release lock after maxDuration
        lockTimeoutRef.current = setTimeout(() => {
            console.warn(`Lock "${reason}" auto-released after ${maxDuration}ms`);
            releaseLock();
        }, maxDuration);

        return true;
    }, [isLocked, lockReason]);

    /**
     * Release the save lock
     */
    const releaseLock = useCallback(() => {
        if (lockTimeoutRef.current) {
            clearTimeout(lockTimeoutRef.current);
            lockTimeoutRef.current = null;
        }
        setIsLocked(false);
        setLockReason(null);
    }, []);

    /**
     * Execute a function with save lock protection
     * @param {Function} fn - Async function to execute
     * @param {string} reason - Lock reason
     * @returns {Promise} Result of the function or null if lock not acquired
     */
    const withLock = useCallback(async (fn, reason = "operation") => {
        if (!acquireLock(reason)) {
            return { success: false, error: "Operation in progress" };
        }

        try {
            const result = await fn();
            return result;
        } catch (error) {
            console.error(`Error during locked operation "${reason}":`, error);
            throw error;
        } finally {
            releaseLock();
        }
    }, [acquireLock, releaseLock]);

    return {
        isLocked,
        lockReason,
        acquireLock,
        releaseLock,
        withLock,
    };
};