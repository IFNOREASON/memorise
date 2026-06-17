import { RETRYABLE_ERROR_CODES, NON_RETRYABLE_ERROR_CODES, ERROR_CATEGORY } from '../constants.js';

export function generateId(prefix = 'id') {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 10);
  return `${prefix}_${timestamp}_${random}`;
}

export function categorizeError(error) {
  const code = error.code || error.errorCode || '';
  const message = error.message || '';
  const status = error.status || error.statusCode || 0;

  if (RETRYABLE_ERROR_CODES.includes(code)) {
    return ERROR_CATEGORY.RETRYABLE;
  }

  if (NON_RETRYABLE_ERROR_CODES.includes(code)) {
    return ERROR_CATEGORY.NON_RETRYABLE;
  }

  if (status >= 500) {
    return ERROR_CATEGORY.RETRYABLE;
  }

  if (status === 429) {
    return ERROR_CATEGORY.RETRYABLE;
  }

  if (status >= 400 && status < 500) {
    return ERROR_CATEGORY.NON_RETRYABLE;
  }

  const retryablePatterns = [
    /rate limit/i,
    /throttl/i,
    /timeout/i,
    /unavailable/i,
    /network/i,
    /connection/i,
    /try again/i,
    /busy/i,
    /overload/i,
  ];

  const nonRetryablePatterns = [
    /invalid format/i,
    /invalid image/i,
    /corrupt/i,
    /unsupported/i,
    /bad request/i,
    /invalid parameter/i,
    /auth/i,
    /permission/i,
    /not found/i,
  ];

  for (const pattern of retryablePatterns) {
    if (pattern.test(message)) {
      return ERROR_CATEGORY.RETRYABLE;
    }
  }

  for (const pattern of nonRetryablePatterns) {
    if (pattern.test(message)) {
      return ERROR_CATEGORY.NON_RETRYABLE;
    }
  }

  return ERROR_CATEGORY.RETRYABLE;
}

export function isRetryableError(error) {
  return categorizeError(error) === ERROR_CATEGORY.RETRYABLE;
}

export function calculateRetryDelay(attempt, config) {
  const {
    INITIAL_RETRY_DELAY_MS,
    MAX_RETRY_DELAY_MS,
    RETRY_BACKOFF_MULTIPLIER,
    RETRY_JITTER_FACTOR,
  } = config;

  const baseDelay = INITIAL_RETRY_DELAY_MS * Math.pow(RETRY_BACKOFF_MULTIPLIER, attempt - 1);
  const cappedDelay = Math.min(baseDelay, MAX_RETRY_DELAY_MS);

  const jitterRange = cappedDelay * RETRY_JITTER_FACTOR;
  const jitter = (Math.random() - 0.5) * jitterRange * 2;

  return Math.max(0, Math.floor(cappedDelay + jitter));
}

export function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function formatDateTime(date) {
  const d = date instanceof Date ? date : new Date(date);
  return d.toISOString();
}

export function now() {
  return new Date().toISOString();
}

export function safeJsonParse(str, fallback = null) {
  try {
    return JSON.parse(str);
  } catch {
    return fallback;
  }
}

export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(deepClone);
  const cloned = {};
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      cloned[key] = deepClone(obj[key]);
    }
  }
  return cloned;
}
