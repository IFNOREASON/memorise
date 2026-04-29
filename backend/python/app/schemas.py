from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any, Dict, Generic, TypeVar
from datetime import datetime
from enum import Enum
import re

T = TypeVar('T')

from app.models import (
    AvatarStatus, GenerationMethod, TaskStatus, PhotoAngle,
    MemoryType, VoiceMaterialStatus, VoiceModelStatus, SynthesisStatus,
    Gender, MemberStatus, MediaType
)


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    confirm_password: str = Field(..., min_length=6, max_length=100, description="确认密码")
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('两次输入的密码不一致')
        return v


class UserLoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=6, max_length=100, alias="currentPassword", description="当前密码")
    new_password: str = Field(..., min_length=6, max_length=100, alias="newPassword", description="新密码")
    confirm_password: str = Field(..., min_length=6, max_length=100, alias="confirmPassword", description="确认新密码")

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('两次输入的新密码不一致')
        return v

    class Config:
        populate_by_name = True


class VerifyPasswordRequest(BaseModel):
    password: str = Field(..., min_length=6, max_length=100, description="密码")

    class Config:
        populate_by_name = True


class UserResponse(BaseModel):
    id: str
    username: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = Field(default=None, alias="avatarUrl")
    is_active: bool = Field(alias="isActive")
    created_at: datetime = Field(alias="createdAt")
    last_login_at: Optional[datetime] = Field(default=None, alias="lastLoginAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str = Field(alias="accessToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    user: UserResponse

    class Config:
        populate_by_name = True


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None


class ConfigInfo(BaseModel):
    aliyun: Dict[str, Any]
    openai: Dict[str, Any]


class PhotoAnalysisResult(BaseModel):
    index: int
    detected_type: str = Field(alias="detectedType")
    detected_type_label: str = Field(alias="detectedTypeLabel")
    confidence: float
    features: List[str]
    quality_score: int = Field(alias="qualityScore")

    class Config:
        populate_by_name = True


class PhotoAnalysisResponse(BaseModel):
    total_photos: int = Field(alias="totalPhotos")
    analysis: List[PhotoAnalysisResult]
    detected_types: List[str] = Field(alias="detectedTypes")
    detected_type_labels: List[str] = Field(alias="detectedTypeLabels")
    missing_types: List[str] = Field(alias="missingTypes")
    missing_type_labels: List[str] = Field(alias="missingTypeLabels")
    overall_quality: int = Field(alias="overallQuality")
    recommendation: str

    class Config:
        populate_by_name = True


class PhotoUploadRequest(BaseModel):
    photos: List[str]


class TextDescription(BaseModel):
    overall: str
    facial_features: List[str] = Field(default_factory=list, alias="facialFeatures")
    hair_styles: List[str] = Field(default_factory=list, alias="hairStyles")
    age_sense: int = Field(default=50, alias="ageSense")
    temperament: str = Field(default="gentle")

    class Config:
        populate_by_name = True


class GenerateAvatarRequest(BaseModel):
    name: str
    relationship: str
    gender: str = "male"
    birth_year: Optional[str] = Field(default=None, alias="birthYear")
    death_year: Optional[str] = Field(default=None, alias="deathYear")
    description: Optional[str] = None
    generation_method: GenerationMethod = Field(default=GenerationMethod.PHOTO, alias="generationMethod")
    photos: List[str] = Field(default_factory=list)
    text_description: Optional[TextDescription] = Field(default=None, alias="textDescription")

    class Config:
        populate_by_name = True


class GenerateAvatarResponse(BaseModel):
    task_id: str = Field(alias="taskId")
    avatar_id: str = Field(alias="avatarId")
    status: str
    message: str

    class Config:
        populate_by_name = True


class AvatarBase(BaseModel):
    id: str
    name: str
    relationship: str
    gender: str
    birth_year: Optional[str] = Field(default=None, alias="birthYear")
    death_year: Optional[str] = Field(default=None, alias="deathYear")
    description: Optional[str] = None
    generation_method: GenerationMethod = Field(alias="generationMethod")
    status: AvatarStatus
    progress: int
    avatar_url: Optional[str] = Field(default=None, alias="avatar")
    model_url: Optional[str] = Field(default=None, alias="modelUrl")
    voice_model_id: Optional[str] = Field(default=None, alias="voiceModelId")
    voice_enabled: bool = Field(default=False, alias="voiceEnabled")
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class AvatarStatusResponse(BaseModel):
    avatar_id: str = Field(alias="avatarId")
    status: AvatarStatus
    progress: int
    generation_method: str = Field(alias="generationMethod")
    estimated_time_remaining: Optional[int] = Field(default=None, alias="estimatedTimeRemaining")

    class Config:
        populate_by_name = True


class AvatarListResponse(BaseModel):
    total: int
    avatars: List[AvatarBase]


class AvatarCreateResponse(BaseModel):
    id: str
    name: str
    relationship: str
    gender: str
    birth_year: Optional[str] = Field(default=None, alias="birthYear")
    death_year: Optional[str] = Field(default=None, alias="deathYear")
    description: Optional[str] = None
    status: AvatarStatus
    progress: int
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True


class UpdateAvatarRequest(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None
    gender: Optional[str] = None
    birth_year: Optional[str] = Field(default=None, alias="birthYear")
    death_year: Optional[str] = Field(default=None, alias="deathYear")
    description: Optional[str] = None

    class Config:
        populate_by_name = True


class FineTuneAdjustments(BaseModel):
    face_width: Optional[int] = Field(default=None, alias="faceWidth")
    jaw_line: Optional[int] = Field(default=None, alias="jawLine")
    cheekbones: Optional[int] = None
    eye_size: Optional[int] = Field(default=None, alias="eyeSize")
    eye_spacing: Optional[int] = Field(default=None, alias="eyeSpacing")
    double_eyelid: Optional[int] = Field(default=None, alias="doubleEyelid")
    nose_size: Optional[int] = Field(default=None, alias="noseSize")
    lip_thickness: Optional[int] = Field(default=None, alias="lipThickness")
    wrinkles: Optional[int] = None

    class Config:
        populate_by_name = True


class FineTuneRequest(BaseModel):
    adjustments: FineTuneAdjustments


class FineTuneResponse(BaseModel):
    success: bool
    avatar_id: str = Field(alias="avatarId")
    status: str

    class Config:
        populate_by_name = True


class MemoryBase(BaseModel):
    id: str
    avatar_id: str = Field(alias="avatarId")
    title: str
    type: MemoryType
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class MemoryCreateRequest(BaseModel):
    avatar_id: str = Field(alias="avatarId")
    title: str
    type: MemoryType
    content: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    meta_data: Optional[Dict[str, Any]] = Field(default=None, alias="metadata")

    class Config:
        populate_by_name = True


class MemoryUpdateRequest(BaseModel):
    title: Optional[str] = None
    type: Optional[MemoryType] = None
    content: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    meta_data: Optional[Dict[str, Any]] = Field(default=None, alias="metadata")


class MemoryListResponse(BaseModel):
    total: int
    memories: List[MemoryBase]


class VoiceMaterialBase(BaseModel):
    id: str
    avatar_id: str = Field(alias="avatarId")
    name: str
    type: str
    format: str
    duration: Optional[int] = None
    size: Optional[int] = None
    status: VoiceMaterialStatus
    quality_score: Optional[int] = Field(default=None, alias="qualityScore")
    transcription: Optional[str] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class VoiceMaterialCreateRequest(BaseModel):
    avatar_id: str = Field(alias="avatarId")
    name: str
    type: str = "upload"
    format: str = "wav"
    duration: Optional[int] = None
    size: Optional[int] = None
    audio_data: Optional[str] = Field(default=None, alias="audioData")

    class Config:
        populate_by_name = True


class VoiceMaterialListResponse(BaseModel):
    total: int
    materials: List[VoiceMaterialBase]


class VoiceModelBase(BaseModel):
    id: str
    avatar_id: str = Field(alias="avatarId")
    name: str
    status: VoiceModelStatus
    progress: int
    material_ids: Optional[List[str]] = Field(default=None, alias="materialIds")
    quality_metrics: Optional[Dict[str, Any]] = Field(default=None, alias="qualityMetrics")
    model_url: Optional[str] = Field(default=None, alias="modelUrl")
    sample_audio_url: Optional[str] = Field(default=None, alias="sampleAudioUrl")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class VoiceModelCreateRequest(BaseModel):
    avatar_id: str = Field(alias="avatarId")
    name: str
    material_ids: List[str] = Field(alias="materialIds")
    config: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True


class VoiceModelListResponse(BaseModel):
    total: int
    models: List[VoiceModelBase]


class VoiceModelStatusResponse(BaseModel):
    model_id: str = Field(alias="modelId")
    status: VoiceModelStatus
    progress: int
    quality_metrics: Optional[Dict[str, Any]] = Field(default=None, alias="qualityMetrics")
    estimated_time_remaining: Optional[int] = Field(default=None, alias="estimatedTimeRemaining")

    class Config:
        populate_by_name = True


class VoiceSynthesisRequest(BaseModel):
    model_id: Optional[str] = Field(default=None, alias="modelId")
    avatar_id: Optional[str] = Field(default=None, alias="avatarId")
    text: str
    options: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True


class VoiceSynthesisResponse(BaseModel):
    task_id: str = Field(alias="taskId")
    model_id: str = Field(alias="modelId")
    avatar_id: str = Field(alias="avatarId")
    text: str
    status: SynthesisStatus
    progress: int
    message: str

    class Config:
        populate_by_name = True


class VoiceSynthesisTask(BaseModel):
    id: str
    model_id: str = Field(alias="modelId")
    avatar_id: str = Field(alias="avatarId")
    text: str
    options: Optional[Dict[str, Any]] = None
    status: SynthesisStatus
    progress: int
    audio_url: Optional[str] = Field(default=None, alias="audioUrl")
    duration: Optional[int] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class BindVoiceModelRequest(BaseModel):
    model_id: str = Field(alias="modelId")

    class Config:
        populate_by_name = True


class ChatMessage(BaseModel):
    id: str
    role: str
    content: str
    timestamp: str


class ChatSessionBase(BaseModel):
    id: str
    avatar_id: str = Field(alias="avatarId")
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class ChatSessionResponse(BaseModel):
    id: str
    avatar_id: str = Field(alias="avatarId")
    avatar_name: str = Field(alias="avatarName")
    avatar_avatar: Optional[str] = Field(default=None, alias="avatarAvatar")
    title: str
    message_count: int = Field(alias="messageCount")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class ChatStreamRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, alias="sessionId")
    avatar_id: str = Field(alias="avatarId")
    messages: List[ChatMessage]

    class Config:
        populate_by_name = True


class ChatSessionCreateRequest(BaseModel):
    avatar_id: str = Field(alias="avatarId")

    class Config:
        populate_by_name = True


class ChatMessageRequest(BaseModel):
    content: str


class ChatMessageResponse(BaseModel):
    user_message: ChatMessage = Field(alias="userMessage")
    assistant_message: ChatMessage = Field(alias="assistantMessage")
    avatar: Dict[str, Any]

    class Config:
        populate_by_name = True


class ChatSessionListResponse(BaseModel):
    total: int
    sessions: List[ChatSessionBase]


class GenerationTaskBase(BaseModel):
    id: str
    avatar_id: str = Field(alias="avatarId")
    task_type: str = Field(alias="taskType")
    status: TaskStatus
    progress: int
    retry_count: int = Field(alias="retryCount")
    max_retries: int = Field(alias="maxRetries")
    last_error: Optional[str] = Field(default=None, alias="lastError")
    next_retry_at: Optional[datetime] = Field(default=None, alias="nextRetryAt")
    external_task_id: Optional[str] = Field(default=None, alias="externalTaskId")
    external_service: Optional[str] = Field(default=None, alias="externalService")
    started_at: Optional[datetime] = Field(default=None, alias="startedAt")
    completed_at: Optional[datetime] = Field(default=None, alias="completedAt")
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class RetryGenerationRequest(BaseModel):
    avatar_id: str = Field(alias="avatarId")

    class Config:
        populate_by_name = True


class HealthResponse(BaseModel):
    status: str
    message: str


class UpdateConfigRequest(BaseModel):
    openai: Optional[Dict[str, Any]] = None
    aliyun: Optional[Dict[str, Any]] = None


class MemberMediaBase(BaseModel):
    id: str
    url: str
    type: MediaType
    date_time: Optional[str] = Field(default=None, alias="dateTime")
    location: Optional[str] = None
    duration: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True


class MemberMediaCreateRequest(BaseModel):
    url: str
    type: MediaType = MediaType.IMAGE
    date_time: Optional[str] = Field(default=None, alias="dateTime")
    location: Optional[str] = None
    duration: Optional[str] = None

    class Config:
        populate_by_name = True


class FamilyMemberBase(BaseModel):
    id: str
    family_id: str = Field(alias="familyId")
    name: str
    gender: Gender
    generation: int
    birth_year: Optional[str] = Field(default=None, alias="birthYear")
    death_year: Optional[str] = Field(default=None, alias="deathYear")
    spouse: Optional[str] = None
    father_id: Optional[str] = Field(default=None, alias="fatherId")
    residence: Optional[str] = None
    note: Optional[str] = None
    status: MemberStatus
    medias: Optional[List[MemberMediaBase]] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class FamilyMemberCreateRequest(BaseModel):
    name: str
    gender: Gender = Gender.MALE
    generation: int = 1
    birth_year: Optional[str] = Field(default=None, alias="birthYear")
    death_year: Optional[str] = Field(default=None, alias="deathYear")
    spouse: Optional[str] = None
    father_id: Optional[str] = Field(default=None, alias="fatherId")
    residence: Optional[str] = None
    note: Optional[str] = None
    status: MemberStatus = MemberStatus.ALIVE

    class Config:
        populate_by_name = True


class FamilyMemberUpdateRequest(BaseModel):
    name: Optional[str] = None
    gender: Optional[Gender] = None
    generation: Optional[int] = None
    birth_year: Optional[str] = Field(default=None, alias="birthYear")
    death_year: Optional[str] = Field(default=None, alias="deathYear")
    spouse: Optional[str] = None
    father_id: Optional[str] = Field(default=None, alias="fatherId")
    residence: Optional[str] = None
    note: Optional[str] = None
    status: Optional[MemberStatus] = None

    class Config:
        populate_by_name = True


class FamilyMemberListResponse(BaseModel):
    total: int
    members: List[FamilyMemberBase]


class FamilyBase(BaseModel):
    id: str
    hall_name: Optional[str] = Field(default=None, alias="hallName")
    surname: str
    ancestor: Optional[str] = None
    description: Optional[str] = None
    zi_bei: Optional[List[str]] = Field(default=None, alias="ziBei")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class FamilyCreateRequest(BaseModel):
    hall_name: Optional[str] = Field(default=None, alias="hallName")
    surname: str
    ancestor: Optional[str] = None
    description: Optional[str] = None
    zi_bei: Optional[List[str]] = Field(default=None, alias="ziBei")

    class Config:
        populate_by_name = True


class FamilyUpdateRequest(BaseModel):
    hall_name: Optional[str] = Field(default=None, alias="hallName")
    surname: Optional[str] = None
    ancestor: Optional[str] = None
    description: Optional[str] = None
    zi_bei: Optional[List[str]] = Field(default=None, alias="ziBei")

    class Config:
        populate_by_name = True


class FamilyDetailResponse(BaseModel):
    family: FamilyBase
    member_count: int = Field(alias="memberCount")
    members: List[FamilyMemberBase]

    class Config:
        populate_by_name = True
