import type {
  ApiResponse,
  Task,
  TaskItem,
  TaskLog,
  PaginatedResponse,
  ImageRepairSubmitPayload,
  GenerationSubmitPayload,
  Message,
  GalleryPhoto,
  FamilyMemory,
} from '../types/task';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'X-User-Id': 'default_user',
};

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      ...DEFAULT_HEADERS,
      ...options.headers,
    },
  });

  const data = await response.json();
  return data as ApiResponse<T>;
}

export const taskApi = {
  submitRepair: (payload: ImageRepairSubmitPayload) =>
    request<{ task: Task; itemCount: number }>('/tasks/repair', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  submitGeneration: (payload: GenerationSubmitPayload) =>
    request<{ task: Task; itemCount: number }>('/tasks/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  list: (params?: {
    limit?: number;
    offset?: number;
    status?: string;
    type?: string;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set('limit', String(params.limit));
    if (params?.offset) searchParams.set('offset', String(params.offset));
    if (params?.status) searchParams.set('status', params.status);
    if (params?.type) searchParams.set('type', params.type);
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return request<PaginatedResponse<Task>>(`/tasks${query}`);
  },

  get: (taskId: string) =>
    request<Task & { items: TaskItem[] }>(`/tasks/${taskId}`),

  cancel: (taskId: string) =>
    request<Task>(`/tasks/${taskId}/cancel`, { method: 'POST' }),

  retry: (taskId: string) =>
    request<Task>(`/tasks/${taskId}/retry`, { method: 'POST' }),

  listItems: (
    taskId: string,
    params?: { limit?: number; offset?: number; status?: string }
  ) => {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set('limit', String(params.limit));
    if (params?.offset) searchParams.set('offset', String(params.offset));
    if (params?.status) searchParams.set('status', params.status);
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return request<PaginatedResponse<TaskItem>>(`/tasks/${taskId}/items${query}`);
  },

  getItem: (itemId: string) => request<TaskItem>(`/tasks/items/${itemId}`),

  listLogs: (
    taskId: string,
    params?: { limit?: number; offset?: number; level?: string }
  ) => {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set('limit', String(params.limit));
    if (params?.offset) searchParams.set('offset', String(params.offset));
    if (params?.level) searchParams.set('level', params.level);
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return request<PaginatedResponse<TaskLog>>(`/tasks/${taskId}/logs${query}`);
  },

  getQueueStats: () => request<any>('/tasks/queue/stats'),
};

export const messageApi = {
  list: (params?: {
    limit?: number;
    offset?: number;
    isRead?: boolean;
    type?: string;
    category?: string;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set('limit', String(params.limit));
    if (params?.offset) searchParams.set('offset', String(params.offset));
    if (params?.isRead !== undefined) searchParams.set('isRead', String(params.isRead));
    if (params?.type) searchParams.set('type', params.type);
    if (params?.category) searchParams.set('category', params.category);
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return request<PaginatedResponse<Message>>(`/messages${query}`);
  },

  get: (messageId: string) => request<Message>(`/messages/${messageId}`),

  markRead: (messageId: string) =>
    request<Message>(`/messages/${messageId}/read`, { method: 'POST' }),

  markAllRead: () =>
    request<{ markedCount: number }>('/messages/read/all', { method: 'POST' }),

  getUnreadCount: () => request<{ count: number }>('/messages/unread/count'),

  delete: (messageId: string) =>
    request<{ deleted: boolean }>(`/messages/${messageId}`, { method: 'DELETE' }),
};

export const galleryApi = {
  getByMember: (
    memberId: string,
    params?: { limit?: number; offset?: number; source?: string; isRepaired?: boolean }
  ) => {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set('limit', String(params.limit));
    if (params?.offset) searchParams.set('offset', String(params.offset));
    if (params?.source) searchParams.set('source', params.source);
    if (params?.isRepaired !== undefined)
      searchParams.set('isRepaired', String(params.isRepaired));
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return request<PaginatedResponse<GalleryPhoto>>(`/gallery/member/${memberId}${query}`);
  },

  getByFamily: (familyId: string, params?: { limit?: number; offset?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set('limit', String(params.limit));
    if (params?.offset) searchParams.set('offset', String(params.offset));
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return request<PaginatedResponse<GalleryPhoto>>(`/gallery/family/${familyId}${query}`);
  },

  get: (photoId: string) => request<GalleryPhoto>(`/gallery/${photoId}`),

  create: (data: Partial<GalleryPhoto>) =>
    request<GalleryPhoto>('/gallery', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (photoId: string, data: Partial<GalleryPhoto>) =>
    request<GalleryPhoto>(`/gallery/${photoId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (photoId: string) =>
    request<{ deleted: boolean }>(`/gallery/${photoId}`, { method: 'DELETE' }),
};

export const familyMemoryApi = {
  getByFamily: (
    familyId: string,
    params?: { limit?: number; offset?: number; type?: string; memberId?: string }
  ) => {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set('limit', String(params.limit));
    if (params?.offset) searchParams.set('offset', String(params.offset));
    if (params?.type) searchParams.set('type', params.type);
    if (params?.memberId) searchParams.set('memberId', params.memberId);
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return request<PaginatedResponse<FamilyMemory>>(`/family-memories/family/${familyId}${query}`);
  },

  get: (memoryId: string) => request<FamilyMemory>(`/family-memories/${memoryId}`),

  create: (data: Partial<FamilyMemory>) =>
    request<FamilyMemory>('/family-memories', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (memoryId: string, data: Partial<FamilyMemory>) =>
    request<FamilyMemory>(`/family-memories/${memoryId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (memoryId: string) =>
    request<{ deleted: boolean }>(`/family-memories/${memoryId}`, { method: 'DELETE' }),
};

export default {
  task: taskApi,
  message: messageApi,
  gallery: galleryApi,
  familyMemory: familyMemoryApi,
};
