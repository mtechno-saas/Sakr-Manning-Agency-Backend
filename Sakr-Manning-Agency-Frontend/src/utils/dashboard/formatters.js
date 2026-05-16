export function formatPhone(value) {
    if (!value) return '';

    // Remove all non-digit characters
    const cleaned = value.replace(/\D/g, '');
    // Format based on length
    if (cleaned.length <= 3) {
        return cleaned;
    } else if (cleaned.length <= 6) {
        return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3)}`;
    } else if (cleaned.length <= 10) {
        return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
    } else {
        return +`${cleaned.slice(0, cleaned.length - 10)} (${cleaned.slice(-10, -7)}) ${cleaned.slice(-7, -4)}-${cleaned.slice(-4)}`;
    }
}
/**

Format IMO number (7 digits)
@example formatIMO('1234567') => '1234567'
*/
export function formatIMO(value) {
    if (!value) return '';

    // Only keep digits, max 7
    const cleaned = value.replace(/\D/g, '').slice(0, 7);
    return cleaned;
}
/**

Format currency
@example formatCurrency(1234.56) => '$1,234.56'
*/
export function formatCurrency(value, currency = 'USD') {
    if (value === null || value === undefined || value === '') return '';

    const num = parseFloat(value);
    if (isNaN(num)) return '';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(num);
}
/**

Format number with commas
@example formatNumber(1234567) => '1,234,567'
*/
export function formatNumber(value) {
    if (value === null || value === undefined || value === '') return '';

    const num = parseFloat(value);
    if (isNaN(num)) return '';
    return new Intl.NumberFormat('en-US').format(num);
}
/**

Parse phone number to clean digits
*/
export function parsePhone(value) {
    if (!value) return '';
    return value.replace(/\D/g, '');
}

/**

Parse currency to number
*/
export function parseCurrency(value) {
    if (!value) return '';
    const cleaned = value.replace(/[^0-9.-]/g, '');
    return cleaned;
}

/**

Capitalize first letter
*/
export function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**

Truncate text with ellipsis
*/
export function truncate(str, length = 50) {
    if (!str) return '';
    if (str.length <= length) return str;
    return str.slice(0, length) + '...';
}

/**

Format file size
@example formatFileSize(1024) => '1 KB'
*/
export function formatFileSize(bytes) {
    if (!bytes) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
export default {
    formatPhone,
    formatIMO,
    formatCurrency,
    formatNumber,
    parsePhone,
    parseCurrency,
    capitalize,
    truncate,
    formatFileSize,
};
