export const TASK_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  RETRYING: 'retrying',
  CANCELLED: 'cancelled',
};

export const TASK_TYPE = {
  IMAGE_REPAIR: 'image_repair',
  AI_GENERATION: 'ai_generation',
  DIGITAL_HUMAN: 'digital_human',
  FINE_TUNE: 'fine_tune',
};

export const ERROR_CATEGORY = {
  RETRYABLE: 'retryable',
  NON_RETRYABLE: 'non_retryable',
};

export const RETRYABLE_ERROR_CODES = [
  'RATE_LIMIT_EXCEEDED',
  'REQUEST_TIMEOUT',
  'SERVICE_UNAVAILABLE',
  'INTERNAL_ERROR',
  'NETWORK_ERROR',
  'CONNECTION_RESET',
  'GATEWAY_TIMEOUT',
  'TOO_MANY_REQUESTS',
];

export const NON_RETRYABLE_ERROR_CODES = [
  'INVALID_IMAGE_FORMAT',
  'INVALID_IMAGE_SIZE',
  'IMAGE_CORRUPTED',
  'INVALID_PARAMETER',
  'AUTHENTICATION_FAILED',
  'PERMISSION_DENIED',
  'NOT_FOUND',
  'BAD_REQUEST',
];

export const TASK_QUEUE_CONFIG = {
  MAX_CONCURRENT_PER_USER: 3,
  MAX_QUEUE_SIZE_PER_USER: 50,
  MAX_RETRY_ATTEMPTS: 5,
  INITIAL_RETRY_DELAY_MS: 2000,
  MAX_RETRY_DELAY_MS: 60000,
  RETRY_BACKOFF_MULTIPLIER: 2,
  RETRY_JITTER_FACTOR: 0.2,
};

export const WEBSOCKET_CONFIG = {
  HEARTBEAT_INTERVAL_MS: 30000,
  CONNECTION_TIMEOUT_MS: 60000,
};

export const POLLING_CONFIG = {
  DEFAULT_INTERVAL_MS: 3000,
  MAX_INTERVAL_MS: 15000,
  BACKOFF_MULTIPLIER: 1.5,
};

export const MESSAGE_TYPE = {
  TASK_PROGRESS: 'task_progress',
  TASK_COMPLETED: 'task_completed',
  TASK_FAILED: 'task_failed',
  TASK_CANCELLED: 'task_cancelled',
  BATCH_COMPLETED: 'batch_completed',
};

export const RELATIONSHIP_TYPE = {
  PARENT_CHILD: 'parent_child',
  SIBLING: 'sibling',
  SPOUSE: 'spouse',
};

export const GALLERY_SOURCE = {
  UPLOAD: 'upload',
  REPAIR: 'repair',
  AI_GENERATION: 'ai_generation',
};
