const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000';

interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

interface Config {
  openai: {
    apiKeyConfigured: boolean;
    baseUrl: string;
    model: string;
  };
  aliyun: {
    apiKeyConfigured: boolean;
    baseUrl: string;
    imageModel: string;
    textModel: string;
  };
}

interface UpdateConfigRequest {
  openai?: {
    apiKey?: string;
    baseUrl?: string;
    model?: string;
  };
  aliyun?: {
    apiKey?: string;
    baseUrl?: string;
    imageModel?: string;
    textModel?: string;
  };
}

interface FineTuneAdjustments {
  faceWidth?: number;
  jawLine?: number;
  cheekbones?: number;
  eyeSize?: number;
  eyeSpacing?: number;
  doubleEyelid?: number;
  noseSize?: number;
  lipThickness?: number;
  wrinkles?: number;
}

interface PhotoAnalysisResult {
  index: number;
  detectedType: 'front' | 'left' | 'right' | 'back' | 'closeup';
  detectedTypeLabel: string;
  confidence: number;
  features: string[];
  qualityScore: number;
}

interface PhotoAnalysisResponse {
  totalPhotos: number;
  analysis: PhotoAnalysisResult[];
  detectedTypes: string[];
  detectedTypeLabels: string[];
  missingTypes: string[];
  missingTypeLabels: string[];
  overallQuality: number;
  recommendation: string;
}

interface GenerateAvatarRequest {
  name: string;
  relationship: string;
  gender: 'male' | 'female';
  birthYear: string;
  deathYear?: string;
  description?: string;
  generationMethod: 'photo' | 'text' | 'manual';
  photos?: string[];
  textDescription?: {
    overall: string;
    facialFeatures: string[];
    hairStyles: string[];
    ageSense: number;
    temperament: string;
  };
  manualAdjust?: {
    faceWidth: number;
    jawLine: number;
    cheekbones: number;
    eyeSize: number;
    eyeSpacing: number;
    doubleEyelid: number;
    noseSize: number;
    lipThickness: number;
    wrinkles: number;
  };
}

interface GenerateAvatarResponse {
  taskId: string;
  avatarId: string;
  status: string;
  message: string;
}

interface AvatarStatusResponse {
  avatarId: string;
  status: 'active' | 'training' | 'generating' | 'inactive';
  progress: number;
  generationMethod: string;
  estimatedTimeRemaining?: number;
}

interface TaskStatusResponse {
  taskId: string;
  avatarId: string;
  status: 'pending' | 'processing' | 'completed';
  progress: number;
  createdAt: string;
}

interface Avatar {
  id: string;
  name: string;
  relationship: string;
  gender: 'male' | 'female';
  birthYear?: string;
  deathYear?: string;
  description?: string;
  generationMethod: 'photo' | 'text' | 'manual';
  status: 'active' | 'training' | 'generating' | 'inactive';
  progress: number;
  avatar?: string;
  modelUrl?: string;
  createdAt: string;
  chatCount?: number;
  voiceModelId?: string;
  voiceEnabled?: boolean;
  voiceBoundAt?: string;
}

type MemoryType = 'text' | 'image' | 'video' | 'richtext' | 'document';

interface Memory {
  id: string;
  avatarId: string;
  title: string;
  type: MemoryType;
  content: string;
  description?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

interface MemoryListItem {
  id: string;
  avatarId: string;
  title: string;
  type: MemoryType;
  description?: string;
  tags?: string[];
  createdAt: string;
  updatedAt: string;
}

interface CreateMemoryRequest {
  avatarId: string;
  title: string;
  type: MemoryType;
  content: string;
  description?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
}

interface UpdateMemoryRequest {
  title?: string;
  type?: MemoryType;
  content?: string;
  description?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
}

interface BatchMemoryResult {
  index: number;
  success: boolean;
  id?: string;
  title?: string;
  error?: string;
}

interface AvatarMemoriesResponse {
  avatarId: string;
  avatarName: string;
  total: number;
  memories: MemoryListItem[];
}

type VoiceMaterialStatus = 'raw' | 'preprocessing' | 'preprocessed';

interface VoiceMaterial {
  id: string;
  avatarId: string;
  name: string;
  type: 'recording' | 'upload';
  format: string;
  duration: number;
  size: number;
  status: VoiceMaterialStatus;
  qualityScore: number;
  transcription: string;
  preprocessInfo?: {
    noiseReduction: string;
    volumeNormalized: boolean;
    silenceRemoved: boolean;
    formatConverted: string;
    processedAt: string;
  };
  createdAt: string;
  updatedAt: string;
}

interface CreateVoiceMaterialRequest {
  avatarId: string;
  name: string;
  type?: 'recording' | 'upload';
  format?: string;
  duration?: number;
  size?: number;
  audioData?: string;
}

type VoiceModelStatus = 'training' | 'ready' | 'failed';

interface VoiceModel {
  id: string;
  avatarId: string;
  name: string;
  status: VoiceModelStatus;
  progress: number;
  materialIds: string[];
  qualityMetrics?: {
    mos: number;
    similarity: number;
    naturalness: number;
  };
  trainingConfig: {
    epochs: number;
    batchSize: number;
    learningRate: number;
  };
  modelPath?: string;
  sampleAudioPath?: string;
  createdAt: string;
  updatedAt: string;
}

interface CreateVoiceModelRequest {
  avatarId: string;
  name: string;
  materialIds: string[];
  config?: {
    epochs?: number;
    batchSize?: number;
    learningRate?: number;
  };
}

interface VoiceModelStatusResponse {
  modelId: string;
  status: VoiceModelStatus;
  progress: number;
  qualityMetrics?: {
    mos: number;
    similarity: number;
    naturalness: number;
  };
  estimatedTimeRemaining?: number;
}

type VoiceSynthesisStatus = 'synthesizing' | 'completed' | 'failed';

interface VoiceSynthesisOptions {
  speed?: number;
  pitch?: number;
  emotion?: 'neutral' | 'happy' | 'sad' | 'angry' | 'calm';
}

interface VoiceSynthesisTask {
  id: string;
  modelId: string;
  avatarId: string;
  text: string;
  options: VoiceSynthesisOptions;
  status: VoiceSynthesisStatus;
  progress: number;
  audioPath?: string;
  duration: number;
  createdAt: string;
  updatedAt: string;
}

interface CreateVoiceSynthesisRequest {
  modelId?: string;
  avatarId?: string;
  text: string;
  options?: VoiceSynthesisOptions;
}

interface BindVoiceModelRequest {
  modelId: string;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ChatSession {
  id: string;
  avatarId: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
}

interface ChatSessionListItem {
  id: string;
  avatarId: string;
  messageCount: number;
  createdAt: string;
  updatedAt: string;
}

interface CreateChatSessionRequest {
  avatarId: string;
}

interface SendChatMessageRequest {
  content: string;
}

interface SendChatMessageResponse {
  userMessage: ChatMessage;
  assistantMessage: ChatMessage;
  avatar: {
    id: string;
    name: string;
    voiceEnabled: boolean;
    voiceModelId?: string;
  };
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          ...options.headers
        },
        ...options
      });

      const responseText = await response.text();

      if (!response.ok) {
        let errorMessage = `请求失败: ${response.status}`;
        if (responseText) {
          try {
            const errorData = JSON.parse(responseText);
            errorMessage = errorData.error || errorMessage;
          } catch {
            errorMessage = responseText.substring(0, 200);
          }
        }
        return {
          success: false,
          error: errorMessage
        };
      }

      const data = JSON.parse(responseText);
      return data as ApiResponse<T>;
    } catch (error) {
      console.error('API 请求错误:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : '网络错误或后端服务未启动'
      };
    }
  }

  async analyzePhotos(photos: string[]): Promise<ApiResponse<PhotoAnalysisResponse>> {
    return this.request<PhotoAnalysisResponse>('/api/photos/analyze', {
      method: 'POST',
      body: JSON.stringify({ photos })
    });
  }

  async generateAvatar(request: GenerateAvatarRequest): Promise<ApiResponse<GenerateAvatarResponse>> {
    return this.request<GenerateAvatarResponse>('/api/avatars/generate', {
      method: 'POST',
      body: JSON.stringify(request)
    });
  }

  async getAvatarStatus(avatarId: string): Promise<ApiResponse<AvatarStatusResponse>> {
    return this.request<AvatarStatusResponse>(`/api/avatars/${avatarId}/status`);
  }

  async getTaskStatus(taskId: string): Promise<ApiResponse<TaskStatusResponse>> {
    return this.request<TaskStatusResponse>(`/api/tasks/${taskId}/status`);
  }

  async getAvatar(avatarId: string): Promise<ApiResponse<Avatar>> {
    return this.request<Avatar>(`/api/avatars/${avatarId}`);
  }

  async getAvatars(): Promise<ApiResponse<{ total: number; avatars: Avatar[] }>> {
    return this.request<{ total: number; avatars: Avatar[] }>('/api/avatars');
  }

  async updateAvatar(
    avatarId: string, 
    updates: Partial<Pick<Avatar, 'name' | 'relationship' | 'gender' | 'birthYear' | 'deathYear' | 'description'>>
  ): Promise<ApiResponse<Avatar>> {
    return this.request<Avatar>(`/api/avatars/${avatarId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
  }

  async deleteAvatar(avatarId: string): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(`/api/avatars/${avatarId}`, {
      method: 'DELETE'
    });
  }

  async checkHealth(): Promise<ApiResponse<{ status: string; message: string }>> {
    return this.request<{ status: string; message: string }>('/api/health');
  }

  async getConfig(): Promise<ApiResponse<Config>> {
    return this.request<Config>('/api/config');
  }

  async updateConfig(config: UpdateConfigRequest): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>('/api/config', {
      method: 'PUT',
      body: JSON.stringify(config)
    });
  }

  async fineTuneAvatar(avatarId: string, adjustments: FineTuneAdjustments): Promise<ApiResponse<{
    success: boolean;
    avatarId: string;
    status: string;
  }>> {
    return this.request<{
      success: boolean;
      avatarId: string;
      status: string;
    }>(`/api/avatars/${avatarId}/fine-tune`, {
      method: 'POST',
      body: JSON.stringify({ adjustments })
    });
  }

  async getMemories(options?: {
    avatarId?: string;
    type?: MemoryType;
    tag?: string;
  }): Promise<ApiResponse<{ total: number; memories: MemoryListItem[] }>> {
    let endpoint = '/api/memories';
    const params = new URLSearchParams();
    
    if (options?.avatarId) params.append('avatarId', options.avatarId);
    if (options?.type) params.append('type', options.type);
    if (options?.tag) params.append('tag', options.tag);
    
    if (params.toString()) {
      endpoint += `?${params.toString()}`;
    }
    
    return this.request<{ total: number; memories: MemoryListItem[] }>(endpoint);
  }

  async getMemory(memoryId: string): Promise<ApiResponse<Memory>> {
    return this.request<Memory>(`/api/memories/${memoryId}`);
  }

  async createMemory(memory: CreateMemoryRequest): Promise<ApiResponse<{
    id: string;
    avatarId: string;
    title: string;
    type: MemoryType;
    createdAt: string;
    message: string;
  }>> {
    return this.request<{
      id: string;
      avatarId: string;
      title: string;
      type: MemoryType;
      createdAt: string;
      message: string;
    }>('/api/memories', {
      method: 'POST',
      body: JSON.stringify(memory)
    });
  }

  async updateMemory(
    memoryId: string, 
    updates: UpdateMemoryRequest
  ): Promise<ApiResponse<{
    id: string;
    title: string;
    type: MemoryType;
    updatedAt: string;
    message: string;
  }>> {
    return this.request<{
      id: string;
      title: string;
      type: MemoryType;
      updatedAt: string;
      message: string;
    }>(`/api/memories/${memoryId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
  }

  async deleteMemory(memoryId: string): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(`/api/memories/${memoryId}`, {
      method: 'DELETE'
    });
  }

  async getAvatarMemories(
    avatarId: string,
    options?: {
      type?: MemoryType;
      tag?: string;
    }
  ): Promise<ApiResponse<AvatarMemoriesResponse>> {
    let endpoint = `/api/avatars/${avatarId}/memories`;
    const params = new URLSearchParams();
    
    if (options?.type) params.append('type', options.type);
    if (options?.tag) params.append('tag', options.tag);
    
    if (params.toString()) {
      endpoint += `?${params.toString()}`;
    }
    
    return this.request<AvatarMemoriesResponse>(endpoint);
  }

  async batchCreateMemories(memories: CreateMemoryRequest[]): Promise<ApiResponse<{
    total: number;
    successCount: number;
    errorCount: number;
    results: BatchMemoryResult[];
    errors: BatchMemoryResult[];
  }>> {
    return this.request<{
      total: number;
      successCount: number;
      errorCount: number;
      results: BatchMemoryResult[];
      errors: BatchMemoryResult[];
    }>('/api/memories/batch', {
      method: 'POST',
      body: JSON.stringify({ memories })
    });
  }

  async getVoiceMaterials(options?: {
    avatarId?: string;
  }): Promise<ApiResponse<{ total: number; materials: VoiceMaterial[] }>> {
    let endpoint = '/api/voice/materials';
    const params = new URLSearchParams();
    
    if (options?.avatarId) params.append('avatarId', options.avatarId);
    
    if (params.toString()) {
      endpoint += `?${params.toString()}`;
    }
    
    return this.request<{ total: number; materials: VoiceMaterial[] }>(endpoint);
  }

  async getVoiceMaterial(materialId: string): Promise<ApiResponse<VoiceMaterial>> {
    return this.request<VoiceMaterial>(`/api/voice/materials/${materialId}`);
  }

  async createVoiceMaterial(material: CreateVoiceMaterialRequest): Promise<ApiResponse<{
    id: string;
    avatarId: string;
    name: string;
    status: VoiceMaterialStatus;
    createdAt: string;
    message: string;
  }>> {
    return this.request<{
      id: string;
      avatarId: string;
      name: string;
      status: VoiceMaterialStatus;
      createdAt: string;
      message: string;
    }>('/api/voice/materials', {
      method: 'POST',
      body: JSON.stringify(material)
    });
  }

  async updateVoiceMaterial(
    materialId: string,
    updates: {
      name?: string;
      transcription?: string;
    }
  ): Promise<ApiResponse<{
    id: string;
    name: string;
    updatedAt: string;
    message: string;
  }>> {
    return this.request<{
      id: string;
      name: string;
      updatedAt: string;
      message: string;
    }>(`/api/voice/materials/${materialId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
  }

  async deleteVoiceMaterial(materialId: string): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(`/api/voice/materials/${materialId}`, {
      method: 'DELETE'
    });
  }

  async preprocessVoiceMaterial(materialId: string): Promise<ApiResponse<{
    materialId: string;
    status: VoiceMaterialStatus;
    message: string;
  }>> {
    return this.request<{
      materialId: string;
      status: VoiceMaterialStatus;
      message: string;
    }>(`/api/voice/materials/${materialId}/preprocess`, {
      method: 'POST'
    });
  }

  async batchPreprocessVoiceMaterials(materialIds: string[]): Promise<ApiResponse<{
    total: number;
    results: Array<{
      materialId: string;
      success: boolean;
      status: string;
    }>;
    message: string;
  }>> {
    return this.request<{
      total: number;
      results: Array<{
        materialId: string;
        success: boolean;
        status: string;
      }>;
      message: string;
    }>('/api/voice/materials/batch-preprocess', {
      method: 'POST',
      body: JSON.stringify({ materialIds })
    });
  }

  async getVoiceModels(options?: {
    avatarId?: string;
  }): Promise<ApiResponse<{ total: number; models: VoiceModel[] }>> {
    let endpoint = '/api/voice/models';
    const params = new URLSearchParams();
    
    if (options?.avatarId) params.append('avatarId', options.avatarId);
    
    if (params.toString()) {
      endpoint += `?${params.toString()}`;
    }
    
    return this.request<{ total: number; models: VoiceModel[] }>(endpoint);
  }

  async getVoiceModel(modelId: string): Promise<ApiResponse<VoiceModel>> {
    return this.request<VoiceModel>(`/api/voice/models/${modelId}`);
  }

  async createVoiceModel(model: CreateVoiceModelRequest): Promise<ApiResponse<{
    modelId: string;
    avatarId: string;
    name: string;
    status: VoiceModelStatus;
    progress: number;
    materialCount: number;
    message: string;
  }>> {
    return this.request<{
      modelId: string;
      avatarId: string;
      name: string;
      status: VoiceModelStatus;
      progress: number;
      materialCount: number;
      message: string;
    }>('/api/voice/models', {
      method: 'POST',
      body: JSON.stringify(model)
    });
  }

  async getVoiceModelStatus(modelId: string): Promise<ApiResponse<VoiceModelStatusResponse>> {
    return this.request<VoiceModelStatusResponse>(`/api/voice/models/${modelId}/status`);
  }

  async deleteVoiceModel(modelId: string): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(`/api/voice/models/${modelId}`, {
      method: 'DELETE'
    });
  }

  async synthesizeVoice(synthesis: CreateVoiceSynthesisRequest): Promise<ApiResponse<{
    taskId: string;
    modelId: string;
    avatarId: string;
    text: string;
    status: VoiceSynthesisStatus;
    progress: number;
    message: string;
  }>> {
    return this.request<{
      taskId: string;
      modelId: string;
      avatarId: string;
      text: string;
      status: VoiceSynthesisStatus;
      progress: number;
      message: string;
    }>('/api/voice/synthesize', {
      method: 'POST',
      body: JSON.stringify(synthesis)
    });
  }

  async getVoiceSynthesisTask(taskId: string): Promise<ApiResponse<VoiceSynthesisTask>> {
    return this.request<VoiceSynthesisTask>(`/api/voice/synthesis/${taskId}`);
  }

  async bindVoiceModelToAvatar(
    avatarId: string,
    modelId: string
  ): Promise<ApiResponse<{
    avatarId: string;
    voiceModelId: string;
    voiceEnabled: boolean;
    voiceBoundAt?: string;
    message: string;
  }>> {
    return this.request<{
      avatarId: string;
      voiceModelId: string;
      voiceEnabled: boolean;
      voiceBoundAt?: string;
      message: string;
    }>(`/api/avatars/${avatarId}/voice-model`, {
      method: 'PUT',
      body: JSON.stringify({ modelId })
    });
  }

  async unbindVoiceModelFromAvatar(
    avatarId: string
  ): Promise<ApiResponse<{
    avatarId: string;
    voiceModelId?: string;
    voiceEnabled: boolean;
    message: string;
  }>> {
    return this.request<{
      avatarId: string;
      voiceModelId?: string;
      voiceEnabled: boolean;
      message: string;
    }>(`/api/avatars/${avatarId}/voice-model`, {
      method: 'DELETE'
    });
  }

  async createChatSession(avatarId: string): Promise<ApiResponse<{
    sessionId: string;
    avatarId: string;
    createdAt: string;
    message: string;
  }>> {
    return this.request<{
      sessionId: string;
      avatarId: string;
      createdAt: string;
      message: string;
    }>('/api/chat/sessions', {
      method: 'POST',
      body: JSON.stringify({ avatarId })
    });
  }

  async getChatSession(sessionId: string): Promise<ApiResponse<ChatSession>> {
    return this.request<ChatSession>(`/api/chat/sessions/${sessionId}`);
  }

  async getChatSessions(avatarId?: string): Promise<ApiResponse<{
    total: number;
    sessions: ChatSessionListItem[];
  }>> {
    let endpoint = '/api/chat/sessions';
    if (avatarId) {
      endpoint += `?avatarId=${encodeURIComponent(avatarId)}`;
    }
    return this.request<{
      total: number;
      sessions: ChatSessionListItem[];
    }>(endpoint);
  }

  async sendChatMessage(
    sessionId: string,
    content: string
  ): Promise<ApiResponse<SendChatMessageResponse>> {
    return this.request<SendChatMessageResponse>(`/api/chat/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content })
    });
  }

  async deleteChatSession(sessionId: string): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(`/api/chat/sessions/${sessionId}`, {
      method: 'DELETE'
    });
  }
}

export const apiService = new ApiService();

export type {
  PhotoAnalysisResult,
  PhotoAnalysisResponse,
  GenerateAvatarRequest,
  GenerateAvatarResponse,
  AvatarStatusResponse,
  TaskStatusResponse,
  Avatar,
  ApiResponse,
  Config,
  UpdateConfigRequest,
  FineTuneAdjustments,
  MemoryType,
  Memory,
  MemoryListItem,
  CreateMemoryRequest,
  UpdateMemoryRequest,
  BatchMemoryResult,
  AvatarMemoriesResponse,
  VoiceMaterial,
  VoiceMaterialStatus,
  CreateVoiceMaterialRequest,
  VoiceModel,
  VoiceModelStatus,
  CreateVoiceModelRequest,
  VoiceModelStatusResponse,
  VoiceSynthesisTask,
  VoiceSynthesisStatus,
  VoiceSynthesisOptions,
  CreateVoiceSynthesisRequest,
  BindVoiceModelRequest,
  ChatMessage,
  ChatSession,
  ChatSessionListItem,
  CreateChatSessionRequest,
  SendChatMessageRequest,
  SendChatMessageResponse
};
