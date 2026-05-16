// utils/retryUtils.js

/**
 * Retry configuration for different operation types
 */
export const RETRY_CONFIG = {
    save: {
        maxAttempts: 3,
        initialDelay: 1000,
        maxDelay: 5000,
        backoffMultiplier: 2,
        retryableErrors: [408, 429, 500, 502, 503, 504],
    },
    load: {
        maxAttempts: 2,
        initialDelay: 500,
        maxDelay: 2000,
        backoffMultiplier: 1.5,
        retryableErrors: [408, 500, 502, 503, 504],
    },
    submit: {
        maxAttempts: 2,
        initialDelay: 2000,
        maxDelay: 5000,
        backoffMultiplier: 2,
        retryableErrors: [408, 500, 502, 503, 504],
    },
};

/**
 * Check if an error is retryable
 * @param {Error} error - Error object
 * @param {number[]} retryableErrors - Array of retryable status codes
 * @returns {boolean}
 */
const isRetryableError = (error, retryableErrors) => {
    // Network errors (no response)
    if (!error.response && error.request) return true;

    // Server errors with retryable status codes
    if (error.response?.status) {
        return retryableErrors.includes(error.response.status);
    }

    return false;
};

/**
 * Calculate delay with exponential backoff
 * @param {number} attempt - Current attempt number (0-indexed)
 * @param {Object} config - Retry configuration
 * @returns {number} Delay in milliseconds
 */
const calculateDelay = (attempt, config) => {
    const delay = config.initialDelay * Math.pow(config.backoffMultiplier, attempt);
    return Math.min(delay, config.maxDelay);
};

/**
 * Sleep utility
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise}
 */
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Retry an async operation with exponential backoff
 * @param {Function} fn - Async function to retry
 * @param {Object} config - Retry configuration
 * @param {Function} onRetry - Optional callback on retry (attempt, error)
 * @returns {Promise} Result of the function
 */
export const retryWithBackoff = async (
    fn,
    configType = "save",
    onRetry = null
) => {
    const config = RETRY_CONFIG[configType] || RETRY_CONFIG.save;
    let lastError;

    for (let attempt = 0; attempt < config.maxAttempts; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;

            // Don't retry if error is not retryable
            if (!isRetryableError(error, config.retryableErrors)) {
                throw error;
            }

            // Don't wait after last attempt
            if (attempt < config.maxAttempts - 1) {
                const delay = calculateDelay(attempt, config);
                onRetry?.(attempt + 1, error, delay);
                await sleep(delay);
            }
        }
    }

    // All retries failed
    throw lastError;
};

/**
 * Retry wrapper with progress tracking
 * @param {Function} fn - Async function to retry
 * @param {Object} options - Configuration options
 * @returns {Promise<{success: boolean, data?: any, error?: string}>}
 */
export const retryOperation = async (fn, options = {}) => {
    const {
        configType = "save",
        operationName = "operation",
        onRetry = null,
        onSuccess = null,
        onError = null,
    } = options;

    try {
        const result = await retryWithBackoff(fn, configType, (attempt, error, delay) => {
            onRetry?.(attempt, error, delay);
        });

        onSuccess?.(result);
        return { success: true, data: result };
    } catch (error) {
        const errorMessage = error.response?.data?.detail
            || error.message
            || "Operation failed";

        console.error(`${operationName} failed after retries:`, error);
        onError?.(error);

        return {
            success: false,
            error: errorMessage,
            retryable: isRetryableError(error, RETRY_CONFIG[configType].retryableErrors),
        };
    }
};

/**
 * Queue for failed operations to retry later
 */
class RetryQueue {
    constructor() {
        this.queue = [];
        this.isProcessing = false;
    }

    add(operation) {
        this.queue.push({
            id: Date.now(),
            operation,
            timestamp: Date.now(),
        });
    }

    async processQueue() {
        if (this.isProcessing || this.queue.length === 0) return;

        this.isProcessing = true;

        while (this.queue.length > 0) {
            const item = this.queue.shift();

            try {
                await item.operation();
            } catch (error) {
                // Re-queue if error is retryable
                if (isRetryableError(error, RETRY_CONFIG.save.retryableErrors)) {
                    this.queue.push(item);
                }
            }

            // Delay between operations
            await sleep(1000);
        }

        this.isProcessing = false;
    }

    getQueuedCount() {
        return this.queue.length;
    }

    clear() {
        this.queue = [];
    }
}

export const retryQueue = new RetryQueue();