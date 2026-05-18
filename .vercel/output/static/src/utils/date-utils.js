/**
 * Date Utility Functions
 * Centralized date formatting and manipulation
 */

/**
 * Format date as relative time (e.g., "2h ago", "5m ago")
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted relative time
 */
export function timeAgo(date) {
    if (!date) return 'agora';
    
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    const now = new Date();
    const diffInSeconds = Math.floor((now - dateObj) / 1000);
    
    if (diffInSeconds < 1) return 'agora';
    if (diffInSeconds < 60) return `${diffInSeconds}s`;
    
    const diffInMinutes = Math.floor(diffInSeconds / 60);
    if (diffInMinutes < 60) return `${diffInMinutes}m`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 30) return `${diffInDays}d`;
    
    const diffInMonths = Math.floor(diffInDays / 30);
    if (diffInMonths < 12) return `${diffInMonths}mes`;
    
    return `${Math.floor(diffInMonths / 12)}ano`;
}

/**
 * Format date as localized string
 * @param {string|Date} date - Date to format
 * @param {Object} options - Intl.DateTimeFormatOptions
 * @returns {string} Formatted date string
 */
export function formatDate(date, options = {}) {
    if (!date) return '';
    
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    const defaults = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return dateObj.toLocaleString('pt-BR', { ...defaults, ...options });
}

/**
 * Get ISO date string from date object
 * @param {string|Date} date - Date to convert
 * @returns {string} ISO date string
 */
export function toISOString(date) {
    if (!date) return null;
    return typeof date === 'string' ? date : new Date(date).toISOString();
}
