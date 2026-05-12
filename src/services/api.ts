const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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

interface RetryAvatarRequest {
  avatarId: string;
}

interface AvatarStatusResponse {
  avatarId: string;
  status: 'active' | 'training' | 'generating' | 'inactive' | 'failed' | 'retry_pending' | 'pending';
  progress: number;
  generationMethod: string;
  estimatedTimeRemaining?: number;
  lastError?: string;
  retryCount?: number;
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
  status: 'active' | 'training' | 'generating' | 'inactive' | 'failed' | 'retry_pending' | 'pending';
  progress: number;
  avatar?: string;
  modelUrl?: string;
  createdAt: string;
  chatCount?: number;
  voiceModelId?: string;
  voiceEnabled?: boolean;
  voiceBoundAt?: string;
  lastError?: string;
  retryCount?: number;
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

type Gender = 'male' | 'female';
type MemberStatus = 'alive' | 'deceased';
type MediaType = 'image' | 'video';

interface MemberMedia {
  id: string;
  url: string;
  type: MediaType;
  dateTime?: string;
  location?: string;
  duration?: string;
}

interface FamilyMember {
  id: string;
  familyId: string;
  name: string;
  gender: Gender;
  generation: number;
  birthYear?: string;
  deathYear?: string;
  spouse?: string;
  fatherId?: string;
  residence?: string;
  note?: string;
  status: MemberStatus;
  medias?: MemberMedia[];
  createdAt: string;
  updatedAt: string;
}

interface Family {
  id: string;
  hallName?: string;
  surname: string;
  ancestor?: string;
  description?: string;
  ziBei?: string[];
  userId?: string;
  createdAt: string;
  updatedAt: string;
}

interface FamilyDetailResponse {
  family: Family;
  memberCount: number;
  members: FamilyMember[];
}

interface CreateFamilyMemberRequest {
  name: string;
  gender?: Gender;
  generation?: number;
  birthYear?: string;
  deathYear?: string;
  spouse?: string;
  fatherId?: string;
  residence?: string;
  note?: string;
  status?: MemberStatus;
}

interface UpdateFamilyMemberRequest {
  name?: string;
  gender?: Gender;
  generation?: number;
  birthYear?: string;
  deathYear?: string;
  spouse?: string;
  fatherId?: string;
  residence?: string;
  note?: string;
  status?: MemberStatus;
}

interface UpdateFamilyRequest {
  hallName?: string;
  surname?: string;
  ancestor?: string;
  description?: string;
  ziBei?: string[];
}

type FamilyRole = 'head' | 'admin' | 'editor' | 'viewer';
type InvitationStatus = 'pending' | 'accepted' | 'rejected' | 'expired';
type ApprovalStatus = 'pending' | 'approved' | 'rejected';
type OperationType = 'create' | 'update' | 'delete' | 'invite' | 'approve' | 'reject' | 'role_change' | 'login' | 'logout';
type TargetType = 'family' | 'family_member' | 'user' | 'invitation' | 'approval' | 'role';

interface FamilyUser {
  id: string;
  familyId: string;
  userId: string;
  role: FamilyRole;
  user?: User;
  createdAt: string;
  updatedAt: string;
}

interface FamilyUserListResponse {
  total: number;
  familyUsers: FamilyUser[];
}

interface ChangeRoleRequest {
  userId: string;
  newRole: FamilyRole;
}

interface Invitation {
  id: string;
  familyId: string;
  inviterId: string;
  inviteeEmail: string;
  inviteeUserId?: string;
  status: InvitationStatus;
  role: FamilyRole;
  message?: string;
  expiresAt: string;
  acceptedAt?: string;
  rejectedAt?: string;
  inviter?: User;
  family?: Family;
  createdAt: string;
  updatedAt: string;
}

interface CreateInvitationRequest {
  inviteeEmail: string;
  role: FamilyRole;
  message?: string;
}

interface InvitationListResponse {
  total: number;
  invitations: Invitation[];
}

interface AcceptInvitationRequest {
  invitationId: string;
}

interface RejectInvitationRequest {
  invitationId: string;
  reason?: string;
}

interface Approval {
  id: string;
  familyId: string;
  requesterId: string;
  approverId?: string;
  targetType: TargetType;
  targetId: string;
  operation: OperationType;
  originalData?: Record<string, unknown>;
  modifiedData: Record<string, unknown>;
  status: ApprovalStatus;
  comment?: string;
  approvedAt?: string;
  rejectedAt?: string;
  rejectionReason?: string;
  requester?: User;
  approver?: User;
  createdAt: string;
  updatedAt: string;
}

interface CreateApprovalRequest {
  targetType: TargetType;
  targetId: string;
  operation: OperationType;
  modifiedData: Record<string, unknown>;
  comment?: string;
}

interface ApprovalProcessRequest {
  approvalId: string;
  action: 'approve' | 'reject';
  reason?: string;
}

interface ApprovalListResponse {
  total: number;
  approvals: Approval[];
}

interface OperationLog {
  id: string;
  familyId?: string;
  userId?: string;
  operation: OperationType;
  targetType?: TargetType;
  targetId?: string;
  description?: string;
  ipAddress?: string;
  userAgent?: string;
  beforeData?: Record<string, unknown>;
  afterData?: Record<string, unknown>;
  user?: User;
  createdAt: string;
}

interface OperationLogListResponse {
  total: number;
  logs: OperationLog[];
}

interface UserFamilyInfo {
  family: Family;
  role: FamilyRole;
  familyUser: FamilyUser;
  memberCount: number;
}

type AnniversaryType = 'birthday' | 'deathday' | 'weddingday' | 'sacrificialday';
type RepeatType = 'yearly' | 'monthly' | 'once';
type PushChannel = 'in_app' | 'email' | 'sms';
type MessageType = 'anniversary_reminder' | 'system_notification';
type MessageStatus = 'unread' | 'read' | 'deleted';
type TaskStatus = 'pending' | 'running' | 'completed' | 'failed';

interface Anniversary {
  id: string;
  familyId: string;
  memberId?: string;
  name: string;
  type: AnniversaryType;
  description?: string;
  date: string;
  year?: number;
  month: number;
  day: number;
  repeatType: RepeatType;
  isLunar: boolean;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

interface AnniversaryCalendarItem {
  id: string;
  name: string;
  type: AnniversaryType;
  date: string;
  year?: number;
  month: number;
  day: number;
  memberId?: string;
  memberName?: string;
  isLunar: boolean;
  description?: string;
}

interface AnniversaryCalendarResponse {
  year: number;
  month: number;
  items: AnniversaryCalendarItem[];
}

interface CreateAnniversaryRequest {
  memberId?: string;
  name: string;
  type: AnniversaryType;
  description?: string;
  date: string;
  year?: number;
  repeatType: RepeatType;
  isLunar: boolean;
}

interface UpdateAnniversaryRequest {
  memberId?: string;
  name?: string;
  type?: AnniversaryType;
  description?: string;
  date?: string;
  year?: number;
  repeatType?: RepeatType;
  isLunar?: boolean;
  isActive?: boolean;
}

interface PushRule {
  id: string;
  familyId: string;
  userId: string;
  anniversaryType?: AnniversaryType;
  pushChannels: PushChannel[];
  advanceDays: number;
  pushTime: string;
  isEnabled: boolean;
  createdAt: string;
  updatedAt: string;
}

interface CreatePushRuleRequest {
  anniversaryType?: AnniversaryType;
  pushChannels: PushChannel[];
  advanceDays: number;
  pushTime: string;
}

interface UpdatePushRuleRequest {
  anniversaryType?: AnniversaryType;
  pushChannels?: PushChannel[];
  advanceDays?: number;
  pushTime?: string;
  isEnabled?: boolean;
}

interface Message {
  id: string;
  userId: string;
  familyId?: string;
  anniversaryId?: string;
  type: MessageType;
  title: string;
  content: string;
  status: MessageStatus;
  readAt?: string;
  createdAt: string;
}

interface MessageListResponse {
  total: number;
  unreadCount: number;
  messages: Message[];
}

interface MarkReadRequest {
  messageIds?: string[];
  markAll?: boolean;
}

type CollaborationLinkStatus = 'active' | 'expired' | 'used' | 'disabled';

interface CollaborationLink {
  id: string;
  familyId: string;
  inviterId: string;
  linkCode: string;
  role: FamilyRole;
  status: CollaborationLinkStatus;
  isVisible: boolean;
  usedCount: number;
  maxUses: number;
  expiresAt?: string;
  usedByUserId?: string;
  usedAt?: string;
  inviter?: User;
  family?: Family;
  createdAt: string;
  updatedAt: string;
}

interface CreateCollaborationLinkRequest {
  role: FamilyRole;
  maxUses: number;
  expiresInDays?: number;
}

interface UpdateCollaborationLinkRequest {
  role?: FamilyRole;
  isVisible?: boolean;
}

interface JoinByLinkRequest {
  linkCode: string;
}

interface CreateFamilyRequest {
  hallName?: string;
  surname: string;
  ancestor?: string;
  description?: string;
  ziBei?: string[];
}

interface UserFamilyListItem {
  family: Family;
  role: FamilyRole;
  familyUser: FamilyUser;
  memberCount: number;
  isHead: boolean;
}

interface MyFamilyStatus {
  hasFamily: boolean;
  families: UserFamilyListItem[];
  ownedFamily?: UserFamilyListItem;
  totalFamilies: number;
}

interface CollaborationLinkListResponse {
  total: number;
  links: CollaborationLink[];
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

interface User {
  id: string;
  username: string;
  nickname?: string;
  avatarUrl?: string;
  isActive: boolean;
  createdAt: string;
  lastLoginAt?: string;
}

interface RegisterRequest {
  username: string;
  password: string;
  confirmPassword: string;
  nickname?: string;
}

interface LoginResponse {
  accessToken: string;
  tokenType: string;
  user: User;
}

interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

interface VerifyPasswordRequest {
  password: string;
}

const FAMILY_ID_KEY = 'memorise_family_id';

class ApiService {
  private currentFamilyId: string | null = null;

  setCurrentFamilyId(familyId: string | null): void {
    this.currentFamilyId = familyId;
    if (familyId) {
      localStorage.setItem(FAMILY_ID_KEY, familyId);
    } else {
      localStorage.removeItem(FAMILY_ID_KEY);
    }
  }

  getCurrentFamilyId(): string | null {
    if (!this.currentFamilyId) {
      this.currentFamilyId = localStorage.getItem(FAMILY_ID_KEY);
    }
    return this.currentFamilyId;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    requireAuth: boolean = false
  ): Promise<ApiResponse<T>> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json; charset=utf-8',
      ...options.headers
    };

    if (requireAuth && authStore.token) {
      headers['Authorization'] = `Bearer ${authStore.token}`;
    }

    const familyId = this.getCurrentFamilyId();
    if (familyId) {
      headers['X-Family-Id'] = familyId;
    }

    try {
      const response = await fetch(url, {
        headers,
        ...options
      });

      const responseText = await response.text();

      if (!response.ok) {
        if (response.status === 401 && requireAuth) {
          console.warn('Token 无效或已过期，正在清除登录状态...');
          authStore.clearAuth();
          
          if (typeof window !== 'undefined') {
            const currentPath = window.location.pathname;
            if (currentPath !== '/login' && currentPath !== '/register') {
              alert('登录已过期，请重新登录');
              window.location.href = '/login';
            }
          }
        }
        
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

  private async authRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, options, true);
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

  async retryAvatar(avatarId: string): Promise<ApiResponse<GenerateAvatarResponse>> {
    return this.request<GenerateAvatarResponse>('/api/avatars/retry', {
      method: 'POST',
      body: JSON.stringify({ avatarId })
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

  async uploadVoiceMaterial(
    avatarId: string,
    name: string,
    audioFile: Blob | File,
    type: 'recording' | 'upload' = 'upload'
  ): Promise<ApiResponse<{
    id: string;
    avatarId: string;
    name: string;
    format: string;
    duration: number;
    size: number;
    status: string;
    createdAt: string;
    message: string;
  }>> {
    const url = `${API_BASE_URL}/api/voice/materials/upload`;
    
    const formData = new FormData();
    formData.append('avatar_id', avatarId);
    formData.append('name', name);
    formData.append('type', type);
    formData.append('audio_file', audioFile);
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData
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
      return data as ApiResponse<{
        id: string;
        avatarId: string;
        name: string;
        format: string;
        duration: number;
        size: number;
        status: string;
        createdAt: string;
        message: string;
      }>;
    } catch (error) {
      console.error('API 请求错误:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : '网络错误或后端服务未启动'
      };
    }
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

  async register(request: RegisterRequest): Promise<ApiResponse<User>> {
    return this.request<User>('/api/register', {
      method: 'POST',
      body: JSON.stringify({
        username: request.username,
        password: request.password,
        confirm_password: request.confirmPassword,
        nickname: request.nickname
      })
    });
  }

  async login(username: string, password: string): Promise<ApiResponse<LoginResponse>> {
    return this.request<LoginResponse>('/api/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
  }

  async changePassword(request: ChangePasswordRequest): Promise<ApiResponse<{ message: string }>> {
    return this.authRequest<{ message: string }>('/api/change-password', {
      method: 'POST',
      body: JSON.stringify({
        currentPassword: request.currentPassword,
        newPassword: request.newPassword,
        confirmPassword: request.confirmPassword
      })
    });
  }

  async verifyPassword(password: string): Promise<ApiResponse<{ message: string }>> {
    return this.authRequest<{ message: string }>('/api/verify-password', {
      method: 'POST',
      body: JSON.stringify({ password })
    });
  }

  async getFamily(): Promise<ApiResponse<FamilyDetailResponse>> {
    return this.authRequest<FamilyDetailResponse>('/api/family');
  }

  async updateFamily(request: UpdateFamilyRequest): Promise<ApiResponse<Family>> {
    return this.authRequest<Family>('/api/family', {
      method: 'PUT',
      body: JSON.stringify(request)
    });
  }

  async getMembers(options?: {
    status?: string;
    search?: string;
  }): Promise<ApiResponse<{ total: number; members: FamilyMember[] }>> {
    let endpoint = '/api/family/members';
    const params = new URLSearchParams();
    
    if (options?.status) params.append('status', options.status);
    if (options?.search) params.append('search', options.search);
    
    if (params.toString()) {
      endpoint += `?${params.toString()}`;
    }
    
    return this.authRequest<{ total: number; members: FamilyMember[] }>(endpoint);
  }

  async getMember(memberId: string): Promise<ApiResponse<FamilyMember>> {
    return this.authRequest<FamilyMember>(`/api/family/members/${memberId}`);
  }

  async createMember(request: CreateFamilyMemberRequest): Promise<ApiResponse<FamilyMember>> {
    return this.authRequest<FamilyMember>('/api/family/members', {
      method: 'POST',
      body: JSON.stringify(request)
    });
  }

  async updateMember(
    memberId: string,
    request: UpdateFamilyMemberRequest
  ): Promise<ApiResponse<FamilyMember>> {
    return this.authRequest<FamilyMember>(`/api/family/members/${memberId}`, {
      method: 'PUT',
      body: JSON.stringify(request)
    });
  }

  async deleteMember(memberId: string): Promise<ApiResponse<{ message: string }>> {
    return this.authRequest<{ message: string }>(`/api/family/members/${memberId}`, {
      method: 'DELETE'
    });
  }

  async getMyFamilyInfo(familyId?: string): Promise<ApiResponse<UserFamilyInfo>> {
    let endpoint = '/api/my/family';
    if (familyId) {
      endpoint += `?familyId=${encodeURIComponent(familyId)}`;
    }
    return this.authRequest<UserFamilyInfo>(endpoint);
  }

  async getFamilyUsers(options?: {
    role?: string;
    search?: string;
  }): Promise<ApiResponse<FamilyUserListResponse>> {
    let endpoint = '/api/family/users';
    const params = new URLSearchParams();
    
    if (options?.role) params.append('role', options.role);
    if (options?.search) params.append('search', options.search);
    
    if (params.toString()) {
      endpoint += `?${params.toString()}`;
    }
    
    return this.authRequest<FamilyUserListResponse>(endpoint);
  }

  async changeUserRole(request: ChangeRoleRequest): Promise<ApiResponse<FamilyUser>> {
    return this.authRequest<FamilyUser>('/api/family/users/role', {
      method: 'PUT',
      body: JSON.stringify(request)
    });
  }

  async createInvitation(request: CreateInvitationRequest): Promise<ApiResponse<Invitation>> {
    return this.authRequest<Invitation>('/api/family/invitations', {
      method: 'POST',
      body: JSON.stringify(request)
    });
  }

  async getInvitations(status?: string): Promise<ApiResponse<InvitationListResponse>> {
    let endpoint = '/api/family/invitations';
    if (status) {
      endpoint += `?status=${encodeURIComponent(status)}`;
    }
    return this.authRequest<InvitationListResponse>(endpoint);
  }

  async getMyInvitations(status?: string): Promise<ApiResponse<InvitationListResponse>> {
    let endpoint = '/api/my/invitations';
    if (status) {
      endpoint += `?status=${encodeURIComponent(status)}`;
    }
    return this.authRequest<InvitationListResponse>(endpoint);
  }

  async acceptInvitation(invitationId: string): Promise<ApiResponse<FamilyUser>> {
    return this.authRequest<FamilyUser>('/api/my/invitations/accept', {
      method: 'POST',
      body: JSON.stringify({ invitationId })
    });
  }

  async rejectInvitation(invitationId: string, reason?: string): Promise<ApiResponse> {
    return this.authRequest<ApiResponse>('/api/my/invitations/reject', {
      method: 'POST',
      body: JSON.stringify({ invitationId, reason })
    });
  }

  async createApproval(request: CreateApprovalRequest): Promise<ApiResponse<Approval>> {
    return this.authRequest<Approval>('/api/approvals', {
      method: 'POST',
      body: JSON.stringify(request)
    });
  }

  async getApprovals(status?: string): Promise<ApiResponse<ApprovalListResponse>> {
    let endpoint = '/api/approvals';
    if (status) {
      endpoint += `?status=${encodeURIComponent(status)}`;
    }
    return this.authRequest<ApprovalListResponse>(endpoint);
  }

  async getPendingApprovals(): Promise<ApiResponse<ApprovalListResponse>> {
    return this.authRequest<ApprovalListResponse>('/api/approvals/pending');
  }

  async getMyApprovals(status?: string): Promise<ApiResponse<ApprovalListResponse>> {
    let endpoint = '/api/approvals/my';
    if (status) {
      endpoint += `?status=${encodeURIComponent(status)}`;
    }
    return this.authRequest<ApprovalListResponse>(endpoint);
  }

  async approveApproval(approvalId: string): Promise<ApiResponse<Approval>> {
    return this.authRequest<Approval>('/api/approvals/approve', {
      method: 'POST',
      body: JSON.stringify({ approvalId, action: 'approve' })
    });
  }

  async rejectApproval(approvalId: string, reason?: string): Promise<ApiResponse<Approval>> {
    return this.authRequest<Approval>('/api/approvals/reject', {
      method: 'POST',
      body: JSON.stringify({ approvalId, action: 'reject', reason })
    });
  }

  async getOperationLogs(options?: {
    operation?: string;
    targetType?: string;
    userId?: string;
    limit?: number;
    offset?: number;
  }): Promise<ApiResponse<OperationLogListResponse>> {
    let endpoint = '/api/logs';
    const params = new URLSearchParams();
    
    if (options?.operation) params.append('operation', options.operation);
    if (options?.targetType) params.append('target_type', options.targetType);
    if (options?.userId) params.append('user_id', options.userId);
    if (options?.limit) params.append('limit', options.limit.toString());
    if (options?.offset) params.append('offset', options.offset.toString());
    
    if (params.toString()) {
      endpoint += `?${params.toString()}`;
    }
    
    return this.authRequest<OperationLogListResponse>(endpoint);
  }

  async getMyOperationLogs(options?: {
    operation?: string;
    targetType?: string;
    limit?: number;
    offset?: number;
  }): Promise<ApiResponse<OperationLogListResponse>> {
    let endpoint = '/api/logs/my';
    const params = new URLSearchParams();
    
    if (options?.operation) params.append('operation', options.operation);
    if (options?.targetType) params.append('target_type', options.targetType);
    if (options?.limit) params.append('limit', options.limit.toString());
    if (options?.offset) params.append('offset', options.offset.toString());
    
    if (params.toString()) {
      endpoint += `?${params.toString()}`;
    }
    
    return this.authRequest<OperationLogListResponse>(endpoint);
  }

  async getMyFamilyStatus(): Promise<ApiResponse<MyFamilyStatus>> {
    return this.authRequest<MyFamilyStatus>('/api/my/family/status');
  }

  async createFamily(request: CreateFamilyRequest): Promise<ApiResponse<UserFamilyInfo>> {
    return this.authRequest<UserFamilyInfo>('/api/family/create', {
      method: 'POST',
      body: JSON.stringify({
        hall_name: request.hallName,
        surname: request.surname,
        ancestor: request.ancestor,
        description: request.description,
        zi_bei: request.ziBei
      })
    });
  }

  async createCollaborationLink(
    request: CreateCollaborationLinkRequest
  ): Promise<ApiResponse<CollaborationLink>> {
    return this.authRequest<CollaborationLink>('/api/collaboration/links', {
      method: 'POST',
      body: JSON.stringify({
        role: request.role,
        maxUses: request.maxUses,
        expiresInDays: request.expiresInDays
      })
    });
  }

  async getCollaborationLinks(status?: string): Promise<ApiResponse<CollaborationLinkListResponse>> {
    let endpoint = '/api/collaboration/links';
    if (status) {
      endpoint += `?status=${encodeURIComponent(status)}`;
    }
    return this.authRequest<CollaborationLinkListResponse>(endpoint);
  }

  async updateCollaborationLink(
    linkId: string,
    request: UpdateCollaborationLinkRequest
  ): Promise<ApiResponse<CollaborationLink>> {
    return this.authRequest<CollaborationLink>(`/api/collaboration/links/${linkId}`, {
      method: 'PUT',
      body: JSON.stringify({
        role: request.role,
        isVisible: request.isVisible
      })
    });
  }

  async resetCollaborationLink(linkId: string): Promise<ApiResponse<CollaborationLink>> {
    return this.authRequest<CollaborationLink>(`/api/collaboration/links/${linkId}/reset`, {
      method: 'POST'
    });
  }

  async joinByLink(linkCode: string): Promise<ApiResponse<UserFamilyInfo>> {
    return this.authRequest<UserFamilyInfo>('/api/collaboration/join', {
      method: 'POST',
      body: JSON.stringify({ linkCode })
    });
  }

  async getAnniversaries(options?: {
    type?: AnniversaryType;
    memberId?: string;
    search?: string;
    isActive?: boolean;
  }): Promise<ApiResponse<{ total: number; anniversaries: Anniversary[] }>> {
    let endpoint = '/api/anniversaries';
    const params = new URLSearchParams();
    
    if (options?.type) params.append('type', options.type);
    if (options?.memberId) params.append('member_id', options.memberId);
    if (options?.search) params.append('search', options.search);
    if (options?.isActive !== undefined) params.append('is_active', options.isActive.toString());
    
    if (params.toString()) {
      endpoint += `?${params.toString()}`;
    }
    
    return this.authRequest<{ total: number; anniversaries: Anniversary[] }>(endpoint);
  }

  async getAnniversary(anniversaryId: string): Promise<ApiResponse<Anniversary>> {
    return this.authRequest<Anniversary>(`/api/anniversaries/${anniversaryId}`);
  }

  async getAnniversariesCalendar(year?: number, month?: number): Promise<ApiResponse<AnniversaryCalendarResponse>> {
    let endpoint = '/api/anniversaries/calendar';
    const params = new URLSearchParams();
    
    if (year) params.append('year', year.toString());
    if (month) params.append('month', month.toString());
    
    if (params.toString()) {
      endpoint += `?${params.toString()}`;
    }
    
    return this.authRequest<AnniversaryCalendarResponse>(endpoint);
  }

  async getUpcomingAnniversaries(days: number = 7): Promise<ApiResponse<AnniversaryCalendarItem[]>> {
    return this.authRequest<AnniversaryCalendarItem[]>(`/api/anniversaries/upcoming?days=${days}`);
  }

  async createAnniversary(request: CreateAnniversaryRequest): Promise<ApiResponse<Anniversary>> {
    return this.authRequest<Anniversary>('/api/anniversaries', {
      method: 'POST',
      body: JSON.stringify(request)
    });
  }

  async updateAnniversary(
    anniversaryId: string,
    request: UpdateAnniversaryRequest
  ): Promise<ApiResponse<Anniversary>> {
    return this.authRequest<Anniversary>(`/api/anniversaries/${anniversaryId}`, {
      method: 'PUT',
      body: JSON.stringify(request)
    });
  }

  async deleteAnniversary(anniversaryId: string): Promise<ApiResponse> {
    return this.authRequest<ApiResponse>(`/api/anniversaries/${anniversaryId}`, {
      method: 'DELETE'
    });
  }

  async getPushRules(options?: {
    anniversaryType?: AnniversaryType;
    isEnabled?: boolean;
  }): Promise<ApiResponse<{ total: number; rules: PushRule[] }>> {
    let endpoint = '/api/push-rules';
    const params = new URLSearchParams();
    
    if (options?.anniversaryType) params.append('anniversary_type', options.anniversaryType);
    if (options?.isEnabled !== undefined) params.append('is_enabled', options.isEnabled.toString());
    
    if (params.toString()) {
      endpoint += `?${params.toString()}`;
    }
    
    return this.authRequest<{ total: number; rules: PushRule[] }>(endpoint);
  }

  async getPushRule(ruleId: string): Promise<ApiResponse<PushRule>> {
    return this.authRequest<PushRule>(`/api/push-rules/${ruleId}`);
  }

  async createPushRule(request: CreatePushRuleRequest): Promise<ApiResponse<PushRule>> {
    return this.authRequest<PushRule>('/api/push-rules', {
      method: 'POST',
      body: JSON.stringify(request)
    });
  }

  async updatePushRule(
    ruleId: string,
    request: UpdatePushRuleRequest
  ): Promise<ApiResponse<PushRule>> {
    return this.authRequest<PushRule>(`/api/push-rules/${ruleId}`, {
      method: 'PUT',
      body: JSON.stringify(request)
    });
  }

  async deletePushRule(ruleId: string): Promise<ApiResponse> {
    return this.authRequest<ApiResponse>(`/api/push-rules/${ruleId}`, {
      method: 'DELETE'
    });
  }

  async getMessages(options?: {
    type?: MessageType;
    status?: MessageStatus;
    limit?: number;
    offset?: number;
  }): Promise<ApiResponse<MessageListResponse>> {
    let endpoint = '/api/messages';
    const params = new URLSearchParams();
    
    if (options?.type) params.append('type', options.type);
    if (options?.status) params.append('status', options.status);
    if (options?.limit) params.append('limit', options.limit.toString());
    if (options?.offset) params.append('offset', options.offset.toString());
    
    if (params.toString()) {
      endpoint += `?${params.toString()}`;
    }
    
    return this.authRequest<MessageListResponse>(endpoint);
  }

  async getMessage(messageId: string): Promise<ApiResponse<Message>> {
    return this.authRequest<Message>(`/api/messages/${messageId}`);
  }

  async getUnreadCount(): Promise<ApiResponse<number>> {
    return this.authRequest<number>('/api/messages/unread-count');
  }

  async markMessagesRead(request: MarkReadRequest): Promise<ApiResponse> {
    return this.authRequest<ApiResponse>('/api/messages/mark-read', {
      method: 'POST',
      body: JSON.stringify(request)
    });
  }

  async deleteMessage(messageId: string): Promise<ApiResponse> {
    return this.authRequest<ApiResponse>(`/api/messages/${messageId}`, {
      method: 'DELETE'
    });
  }

  async deleteAllMessages(): Promise<ApiResponse> {
    return this.authRequest<ApiResponse>('/api/messages', {
      method: 'DELETE'
    });
  }

  async previewImport(formData: FormData): Promise<ApiResponse<{ preview: any[] }>> {
    const url = `${API_BASE_URL}/api/family/import/preview`;
    const token = authStore.token;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Family-Id': this.getCurrentFamilyId() || ''
        },
        body: formData
      });

      const data = await response.json();
      return data as ApiResponse<{ preview: any[] }>;
    } catch (error) {
      console.error('API 请求错误:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : '网络错误或后端服务未启动'
      };
    }
  }

  async importData(formData: FormData): Promise<ApiResponse<{ count: number; members: any[] }>> {
    const url = `${API_BASE_URL}/api/family/import`;
    const token = authStore.token;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Family-Id': this.getCurrentFamilyId() || ''
        },
        body: formData
      });

      const data = await response.json();
      return data as ApiResponse<{ count: number; members: any[] }>;
    } catch (error) {
      console.error('API 请求错误:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : '网络错误或后端服务未启动'
      };
    }
  }

  async exportData(format: 'xlsx' | 'csv' = 'xlsx'): Promise<Blob> {
    const url = `${API_BASE_URL}/api/family/export?format=${format}`;
    const token = authStore.token;
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Family-Id': this.getCurrentFamilyId() || ''
        }
      });

      if (!response.ok) {
        throw new Error('导出失败');
      }

      return await response.blob();
    } catch (error) {
      console.error('导出失败:', error);
      throw error;
    }
  }
}

const TOKEN_KEY = 'memorise_token';
const USER_KEY = 'memorise_user';

interface AuthStore {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setToken: (token: string) => void;
  setUser: (user: User) => void;
  clearAuth: () => void;
  loadFromStorage: () => void;
}

const createAuthStore = (): AuthStore => {
  const store: AuthStore = {
    token: null,
    user: null,
    isAuthenticated: false,

    setToken(token: string) {
      this.token = token;
      this.isAuthenticated = !!token;
      if (token) {
        localStorage.setItem(TOKEN_KEY, token);
      } else {
        localStorage.removeItem(TOKEN_KEY);
      }
    },

    setUser(user: User) {
      this.user = user;
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    },

    clearAuth() {
      this.token = null;
      this.user = null;
      this.isAuthenticated = false;
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      localStorage.removeItem(FAMILY_ID_KEY);
      apiService.setCurrentFamilyId(null);
    },

    loadFromStorage() {
      const token = localStorage.getItem(TOKEN_KEY);
      const userStr = localStorage.getItem(USER_KEY);

      if (token) {
        this.token = token;
        this.isAuthenticated = true;
      }

      if (userStr) {
        try {
          this.user = JSON.parse(userStr);
        } catch {
          this.user = null;
        }
      }
    }
  };

  store.loadFromStorage();
  return store;
};

export const authStore = createAuthStore();

export const apiService = new ApiService();

export type {
  User,
  RegisterRequest,
  LoginResponse,
  ChangePasswordRequest,
  VerifyPasswordRequest,
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
  SendChatMessageResponse,
  UserFamilyListItem,
  MyFamilyStatus
};
