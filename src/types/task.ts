export const TaskStatus = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  RETRYING: 'retrying',
  CANCELLED: 'cancelled',
} as const;

export type TaskStatus = (typeof TaskStatus)[keyof typeof TaskStatus];

export const TaskType = {
  IMAGE_REPAIR: 'image_repair',
  AI_GENERATION: 'ai_generation',
  DIGITAL_HUMAN: 'digital_human',
  FINE_TUNE: 'fine_tune',
} as const;

export type TaskType = (typeof TaskType)[keyof typeof TaskType];

export const ErrorCategory = {
  RETRYABLE: 'retryable',
  NON_RETRYABLE: 'non_retryable',
} as const;

export type ErrorCategory = (typeof ErrorCategory)[keyof typeof ErrorCategory];

export const MessageType = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
} as const;

export type MessageType = (typeof MessageType)[keyof typeof MessageType];

export const GallerySource = {
  UPLOAD: 'upload',
  REPAIR: 'repair',
  AI_GENERATION: 'ai_generation',
} as const;

export type GallerySource = (typeof GallerySource)[keyof typeof GallerySource];

export interface Task {
  id: string;
  userId: string;
  familyId: string | null;
  memberId: string | null;
  type: TaskType;
  title: string;
  description: string;
  status: TaskStatus;
  totalItems: number;
  completedItems: number;
  failedItems: number;
  progress: number;
  priority: number;
  metadata: Record<string, any>;
  result: any;
  error: any;
  createdAt: string;
  updatedAt: string;
  startedAt: string | null;
  completedAt: string | null;
  cancelledAt: string | null;
  items?: TaskItem[];
}

export interface TaskItem {
  id: string;
  taskId: string;
  userId: string;
  type: TaskType;
  index: number;
  title: string;
  inputData: Record<string, any>;
  outputData: any;
  status: TaskStatus;
  error: {
    message: string;
    code: string;
  } | null;
  errorCategory: ErrorCategory | null;
  retryCount: number;
  maxRetries: number;
  nextRetryAt: string | null;
  metadata: Record<string, any>;
  createdAt: string;
  updatedAt: string;
  startedAt: string | null;
  completedAt: string | null;
}

export interface TaskLog {
  id: string;
  taskId: string | null;
  itemId: string | null;
  userId: string;
  level: 'info' | 'warn' | 'error' | 'debug';
  action: string;
  message: string;
  details: Record<string, any>;
  timestamp: string;
}

export interface Message {
  id: string;
  userId: string;
  type: MessageType;
  title: string;
  content: string;
  category: string;
  taskId: string | null;
  itemId: string | null;
  actionUrl: string | null;
  actionText: string | null;
  metadata: Record<string, any>;
  isRead: boolean;
  createdAt: string;
  readAt: string | null;
}

export interface GalleryPhoto {
  id: string;
  userId: string;
  familyId: string | null;
  memberId: string | null;
  title: string;
  description: string;
  imageUrl: string;
  thumbnailUrl: string;
  source: GallerySource;
  sourceTaskId: string | null;
  sourceItemId: string | null;
  originalPhotoId: string | null;
  repairedPhotoId: string | null;
  isRepaired: boolean;
  isAIGenerated: boolean;
  tags: string[];
  metadata: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export interface FamilyMemory {
  id: string;
  userId: string;
  familyId: string | null;
  memberId: string | null;
  title: string;
  description: string;
  content: string;
  date: string | null;
  location: string;
  type: string;
  photoIds: string[];
  beforeAfterPairs: Array<{
    beforeUrl: string;
    afterUrl: string;
    beforeId: string | null;
    afterId: string | null;
    title: string;
    stats?: any;
  }>;
  sourceTaskId: string | null;
  tags: string[];
  metadata: Record<string, any>;
  isPublished: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface RepairOptions {
  mode?: 'basic' | 'enhance' | 'colorize' | 'full';
  enableScratchRemoval?: boolean;
  enableColorize?: boolean;
  enableFaceEnhance?: boolean;
  targetResolution?: string;
}

export interface ImageRepairSubmitPayload {
  images: Array<{
    url: string;
    photoId?: string;
    title?: string;
    description?: string;
  }>;
  familyId?: string | null;
  memberId?: string | null;
  title?: string;
  description?: string;
  repairOptions?: RepairOptions;
  autoAddToGallery?: boolean;
  autoCreateMemory?: boolean;
  maxRetries?: number;
  priority?: number;
}

export interface GenerationSubmitPayload {
  type?: string;
  prompt: string;
  familyId?: string | null;
  memberId?: string | null;
  title?: string;
  description?: string;
  generationOptions?: Record<string, any>;
  numImages?: number;
  autoAddToGallery?: boolean;
  maxRetries?: number;
  priority?: number;
}

export interface PaginatedResponse<T> {
  total: number;
  items: T[];
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: {
    code: string;
    message: string;
  };
}

export interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp: string;
}

export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  [TaskStatus.PENDING]: '排队中',
  [TaskStatus.PROCESSING]: '处理中',
  [TaskStatus.COMPLETED]: '已完成',
  [TaskStatus.FAILED]: '失败',
  [TaskStatus.RETRYING]: '重试中',
  [TaskStatus.CANCELLED]: '已取消',
};

export const TASK_TYPE_LABELS: Record<TaskType, string> = {
  [TaskType.IMAGE_REPAIR]: '照片修复',
  [TaskType.AI_GENERATION]: 'AI生成',
  [TaskType.DIGITAL_HUMAN]: '数字人',
  [TaskType.FINE_TUNE]: '模型微调',
};

export const TASK_STATUS_COLORS: Record<TaskStatus, string> = {
  [TaskStatus.PENDING]: '#9CA3AF',
  [TaskStatus.PROCESSING]: '#3B82F6',
  [TaskStatus.COMPLETED]: '#10B981',
  [TaskStatus.FAILED]: '#EF4444',
  [TaskStatus.RETRYING]: '#F59E0B',
  [TaskStatus.CANCELLED]: '#6B7280',
};
