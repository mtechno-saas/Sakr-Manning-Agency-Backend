// utils/dateHelpers.js
/**

Date utility functions
*/

/**

Format date to YYYY-MM-DD
*/
export function formatDate(date) {
    if (!date) return '';
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/**

Format date for display (e.g., "Jan 15, 2024")
*/
export function formatDateDisplay(date) {
    if (!date) return '';
    const d = new Date(date);
    return d.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    });
}

/**

Get today's date in YYYY-MM-DD format
*/
export function getToday() {
    return formatDate(new Date());
}

/**

Get tomorrow's date in YYYY-MM-DD format
*/
export function getTomorrow() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return formatDate(tomorrow);
}

/**

Add days to a date
*/
export function addDays(date, days) {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return formatDate(result);
}

/**

Add months to a date
*/
export function addMonths(date, months) {
    const result = new Date(date);
    result.setMonth(result.getMonth() + months);
    return formatDate(result);
}

/**

Calculate days between two dates
*/
export function daysBetween(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

/**

Calculate months between two dates (approximate)
*/
export function monthsBetween(startDate, endDate) {
    const days = daysBetween(startDate, endDate);
    return Math.round(days / 30);
}

/**

Check if date is in the past
*/
export function isPastDate(date) {
    const d = new Date(date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return d < today;
}

/**

Check if date is in the future
*/
export function isFutureDate(date) {
    const d = new Date(date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return d > today;
}

/**

Check if date is today
*/
export function isToday(date) {
    const d = new Date(date);
    const today = new Date();
    return (
        d.getDate() === today.getDate() &&
        d.getMonth() === today.getMonth() &&
        d.getFullYear() === today.getFullYear()
    );
}

/**

Get date range presets
*/
export const datePresets = {
    today: () => ({
        start: getToday(),
        end: getToday(),
    }),
    tomorrow: () => ({
        start: getTomorrow(),
        end: getTomorrow(),
    }),
    nextWeek: () => ({
        start: addDays(new Date(), 7),
        end: addDays(new Date(), 7),
    }),
    nextMonth: () => ({
        start: addMonths(new Date(), 1),
        end: addMonths(new Date(), 1),
    }),
    next3Months: () => ({
        start: getToday(),
        end: addMonths(new Date(), 3),
    }),
    next6Months: () => ({
        start: getToday(),
        end: addMonths(new Date(), 6),
    }),
    next12Months: () => ({
        start: getToday(),
        end: addMonths(new Date(), 12),
    }),
};

export default {
    formatDate,
    formatDateDisplay,
    getToday,
    getTomorrow,
    addDays,
    addMonths,
    daysBetween,
    monthsBetween,
    isPastDate,
    isFutureDate,
    isToday,
    datePresets,
};
