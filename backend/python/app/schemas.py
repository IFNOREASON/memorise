from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any, Dict, Generic, TypeVar
from datetime import datetime
import enum
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
    chat_count: Optional[int] = Field(default=None, alias="chatCount")

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


class TaskStatusResponse(BaseModel):
    task_id: str = Field(alias="taskId")
    avatar_id: str = Field(alias="avatarId")
    status: TaskStatus
    progress: int
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True
        from_attributes = True


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


class HomeStatsResponse(BaseModel):
    member_count: int = Field(alias="memberCount")
    gallery_count: int = Field(alias="galleryCount")
    avatar_count: int = Field(alias="avatarCount")
    
    class Config:
        populate_by_name = True


class FamilyRole(str, enum.Enum):
    HEAD = "head"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class OperationType(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    INVITE = "invite"
    APPROVE = "approve"
    REJECT = "reject"
    ROLE_CHANGE = "role_change"
    LOGIN = "login"
    LOGOUT = "logout"


class TargetType(str, enum.Enum):
    FAMILY = "family"
    FAMILY_MEMBER = "family_member"
    USER = "user"
    INVITATION = "invitation"
    APPROVAL = "approval"
    ROLE = "role"


class FamilyUserBase(BaseModel):
    id: str
    family_id: str = Field(alias="familyId")
    user_id: str = Field(alias="userId")
    role: FamilyRole
    user: Optional[UserResponse] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class FamilyUserListResponse(BaseModel):
    total: int
    familyUsers: List[FamilyUserBase] = Field(alias="familyUsers")


class ChangeRoleRequest(BaseModel):
    user_id: str = Field(alias="userId")
    new_role: FamilyRole = Field(alias="newRole")

    class Config:
        populate_by_name = True


class InvitationBase(BaseModel):
    id: str
    family_id: str = Field(alias="familyId")
    inviter_id: str = Field(alias="inviterId")
    invitee_email: str = Field(alias="inviteeEmail")
    invitee_user_id: Optional[str] = Field(default=None, alias="inviteeUserId")
    status: InvitationStatus
    role: FamilyRole
    message: Optional[str] = None
    expires_at: datetime = Field(alias="expiresAt")
    accepted_at: Optional[datetime] = Field(default=None, alias="acceptedAt")
    rejected_at: Optional[datetime] = Field(default=None, alias="rejectedAt")
    inviter: Optional[UserResponse] = None
    family: Optional[FamilyBase] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class InvitationCreateRequest(BaseModel):
    invitee_email: str = Field(alias="inviteeEmail")
    role: FamilyRole = FamilyRole.VIEWER
    message: Optional[str] = None

    class Config:
        populate_by_name = True


class InvitationListResponse(BaseModel):
    total: int
    invitations: List[InvitationBase]


class AcceptInvitationRequest(BaseModel):
    invitation_id: str = Field(alias="invitationId")

    class Config:
        populate_by_name = True


class RejectInvitationRequest(BaseModel):
    invitation_id: str = Field(alias="invitationId")
    reason: Optional[str] = None

    class Config:
        populate_by_name = True


class ApprovalBase(BaseModel):
    id: str
    family_id: str = Field(alias="familyId")
    requester_id: str = Field(alias="requesterId")
    approver_id: Optional[str] = Field(default=None, alias="approverId")
    target_type: TargetType = Field(alias="targetType")
    target_id: str = Field(alias="targetId")
    operation: OperationType
    original_data: Optional[Dict[str, Any]] = Field(default=None, alias="originalData")
    modified_data: Dict[str, Any] = Field(alias="modifiedData")
    status: ApprovalStatus
    comment: Optional[str] = None
    approved_at: Optional[datetime] = Field(default=None, alias="approvedAt")
    rejected_at: Optional[datetime] = Field(default=None, alias="rejectedAt")
    rejection_reason: Optional[str] = Field(default=None, alias="rejectionReason")
    requester: Optional[UserResponse] = None
    approver: Optional[UserResponse] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class ApprovalCreateRequest(BaseModel):
    target_type: TargetType = Field(alias="targetType")
    target_id: str = Field(alias="targetId")
    operation: OperationType
    modified_data: Dict[str, Any] = Field(alias="modifiedData")
    comment: Optional[str] = None

    class Config:
        populate_by_name = True


class ApprovalProcessRequest(BaseModel):
    approval_id: str = Field(alias="approvalId")
    action: str
    reason: Optional[str] = None

    class Config:
        populate_by_name = True


class ApprovalListResponse(BaseModel):
    total: int
    approvals: List[ApprovalBase]


class OperationLogBase(BaseModel):
    id: str
    family_id: Optional[str] = Field(default=None, alias="familyId")
    user_id: Optional[str] = Field(default=None, alias="userId")
    operation: OperationType
    target_type: Optional[TargetType] = Field(default=None, alias="targetType")
    target_id: Optional[str] = Field(default=None, alias="targetId")
    description: Optional[str] = None
    ip_address: Optional[str] = Field(default=None, alias="ipAddress")
    user_agent: Optional[str] = Field(default=None, alias="userAgent")
    before_data: Optional[Dict[str, Any]] = Field(default=None, alias="beforeData")
    after_data: Optional[Dict[str, Any]] = Field(default=None, alias="afterData")
    user: Optional[UserResponse] = None
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class OperationLogListResponse(BaseModel):
    total: int
    logs: List[OperationLogBase]


class UserFamilyInfo(BaseModel):
    family: FamilyBase
    role: FamilyRole
    familyUser: FamilyUserBase = Field(alias="familyUser")
    memberCount: int = Field(alias="memberCount")

    class Config:
        populate_by_name = True


class UserFamilyListItem(BaseModel):
    family: FamilyBase
    role: FamilyRole
    familyUser: FamilyUserBase = Field(alias="familyUser")
    memberCount: int = Field(alias="memberCount")
    isHead: bool = Field(alias="isHead")

    class Config:
        populate_by_name = True


class MyFamilyStatus(BaseModel):
    hasFamily: bool = Field(alias="hasFamily")
    families: List[UserFamilyListItem] = Field(default_factory=list, alias="families")
    ownedFamily: Optional[UserFamilyListItem] = Field(default=None, alias="ownedFamily")
    totalFamilies: int = Field(default=0, alias="totalFamilies")

    class Config:
        populate_by_name = True


class CollaborationLinkStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    USED = "used"
    DISABLED = "disabled"


class CollaborationLinkBase(BaseModel):
    id: str
    familyId: str = Field(alias="familyId")
    inviterId: str = Field(alias="inviterId")
    linkCode: str = Field(alias="linkCode")
    role: FamilyRole
    status: CollaborationLinkStatus
    isVisible: bool = Field(alias="isVisible")
    usedCount: int = Field(alias="usedCount")
    maxUses: int = Field(alias="maxUses")
    expiresAt: Optional[datetime] = Field(default=None, alias="expiresAt")
    usedByUserId: Optional[str] = Field(default=None, alias="usedByUserId")
    usedAt: Optional[datetime] = Field(default=None, alias="usedAt")
    inviter: Optional[UserResponse] = None
    family: Optional[FamilyBase] = None
    createdAt: datetime = Field(alias="createdAt")
    updatedAt: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class CreateCollaborationLinkRequest(BaseModel):
    role: FamilyRole = FamilyRole.VIEWER
    maxUses: int = Field(default=1, alias="maxUses", ge=1)
    expiresInDays: Optional[int] = Field(default=None, alias="expiresInDays", ge=1)

    class Config:
        populate_by_name = True


class UpdateCollaborationLinkRequest(BaseModel):
    role: Optional[FamilyRole] = None
    isVisible: Optional[bool] = Field(default=None, alias="isVisible")

    class Config:
        populate_by_name = True


class JoinByLinkRequest(BaseModel):
    linkCode: str = Field(alias="linkCode")

    class Config:
        populate_by_name = True


class CollaborationLinkListResponse(BaseModel):
    total: int
    links: List[CollaborationLinkBase]


class AnniversaryType(str, enum.Enum):
    BIRTHDAY = "birthday"
    DEATHDAY = "deathday"
    WEDDINGDAY = "weddingday"
    SACRIFICIALDAY = "sacrificialday"


class RepeatType(str, enum.Enum):
    YEARLY = "yearly"
    MONTHLY = "monthly"
    ONCE = "once"


class PushChannel(str, enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"


class MessageType(str, enum.Enum):
    ANNIVERSARY_REMINDER = "anniversary_reminder"
    SYSTEM_NOTIFICATION = "system_notification"


class MessageStatus(str, enum.Enum):
    UNREAD = "unread"
    READ = "read"
    DELETED = "deleted"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AnniversaryBase(BaseModel):
    id: str
    family_id: str = Field(alias="familyId")
    member_id: Optional[str] = Field(default=None, alias="memberId")
    name: str
    type: AnniversaryType
    description: Optional[str] = None
    date: str
    year: Optional[int] = None
    month: int
    day: int
    repeat_type: RepeatType = Field(alias="repeatType")
    is_lunar: bool = Field(default=False, alias="isLunar")
    is_active: bool = Field(default=True, alias="isActive")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class AnniversaryCreateRequest(BaseModel):
    member_id: Optional[str] = Field(default=None, alias="memberId")
    name: str
    type: AnniversaryType = AnniversaryType.BIRTHDAY
    description: Optional[str] = None
    date: str
    year: Optional[int] = None
    repeat_type: RepeatType = Field(default=RepeatType.YEARLY, alias="repeatType")
    is_lunar: bool = Field(default=False, alias="isLunar")

    class Config:
        populate_by_name = True


class AnniversaryUpdateRequest(BaseModel):
    member_id: Optional[str] = Field(default=None, alias="memberId")
    name: Optional[str] = None
    type: Optional[AnniversaryType] = None
    description: Optional[str] = None
    date: Optional[str] = None
    year: Optional[int] = None
    repeat_type: Optional[RepeatType] = Field(default=None, alias="repeatType")
    is_lunar: Optional[bool] = Field(default=None, alias="isLunar")
    is_active: Optional[bool] = Field(default=None, alias="isActive")

    class Config:
        populate_by_name = True


class AnniversaryListResponse(BaseModel):
    total: int
    anniversaries: List[AnniversaryBase]


class AnniversaryCalendarItem(BaseModel):
    id: str
    name: str
    type: AnniversaryType
    date: str
    year: Optional[int] = None
    month: int
    day: int
    member_id: Optional[str] = Field(default=None, alias="memberId")
    member_name: Optional[str] = Field(default=None, alias="memberName")
    is_lunar: bool = Field(alias="isLunar")
    description: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True


class AnniversaryCalendarResponse(BaseModel):
    year: int
    month: int
    items: List[AnniversaryCalendarItem]


class PushRuleBase(BaseModel):
    id: str
    family_id: str = Field(alias="familyId")
    user_id: str = Field(alias="userId")
    anniversary_type: Optional[AnniversaryType] = Field(default=None, alias="anniversaryType")
    push_channels: List[PushChannel] = Field(alias="pushChannels")
    advance_days: int = Field(default=0, alias="advanceDays")
    push_time: str = Field(default="09:00", alias="pushTime")
    is_enabled: bool = Field(default=True, alias="isEnabled")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class PushRuleCreateRequest(BaseModel):
    anniversary_type: Optional[AnniversaryType] = Field(default=None, alias="anniversaryType")
    push_channels: List[PushChannel] = Field(alias="pushChannels")
    advance_days: int = Field(default=0, alias="advanceDays")
    push_time: str = Field(default="09:00", alias="pushTime")

    class Config:
        populate_by_name = True


class PushRuleUpdateRequest(BaseModel):
    anniversary_type: Optional[AnniversaryType] = Field(default=None, alias="anniversaryType")
    push_channels: Optional[List[PushChannel]] = Field(default=None, alias="pushChannels")
    advance_days: Optional[int] = Field(default=None, alias="advanceDays")
    push_time: Optional[str] = Field(default=None, alias="pushTime")
    is_enabled: Optional[bool] = Field(default=None, alias="isEnabled")

    class Config:
        populate_by_name = True


class PushRuleListResponse(BaseModel):
    total: int
    rules: List[PushRuleBase]


class MessageBase(BaseModel):
    id: str
    user_id: str = Field(alias="userId")
    family_id: Optional[str] = Field(default=None, alias="familyId")
    anniversary_id: Optional[str] = Field(default=None, alias="anniversaryId")
    type: MessageType
    title: str
    content: str
    status: MessageStatus
    read_at: Optional[datetime] = Field(default=None, alias="readAt")
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class MessageListResponse(BaseModel):
    total: int
    unread_count: int = Field(alias="unreadCount")
    messages: List[MessageBase]


class MessageMarkReadRequest(BaseModel):
    message_ids: Optional[List[str]] = Field(default=None, alias="messageIds")
    mark_all: bool = Field(default=False, alias="markAll")

    class Config:
        populate_by_name = True


class ScheduledTaskBase(BaseModel):
    id: str
    task_name: str = Field(alias="taskName")
    task_type: str = Field(alias="taskType")
    anniversary_id: Optional[str] = Field(default=None, alias="anniversaryId")
    user_id: Optional[str] = Field(default=None, alias="userId")
    scheduled_time: datetime = Field(alias="scheduledTime")
    executed_at: Optional[datetime] = Field(default=None, alias="executedAt")
    status: TaskStatus
    result: Optional[str] = None
    error_message: Optional[str] = Field(default=None, alias="errorMessage")
    retry_count: int = Field(alias="retryCount")
    max_retries: int = Field(alias="maxRetries")

    class Config:
        populate_by_name = True
        from_attributes = True


class ScheduledTaskListResponse(BaseModel):
    total: int
    tasks: List[ScheduledTaskBase]


class GalleryStatus(str, enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"


class GalleryType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"


class GalleryMediaBase(BaseModel):
    id: str
    gallery_id: str = Field(alias="galleryId")
    url: str
    type: MediaType
    date_time: Optional[str] = Field(default=None, alias="dateTime")
    location: Optional[str] = None
    duration: Optional[str] = None
    audio_url: Optional[str] = Field(default=None, alias="audioUrl")
    description: Optional[str] = None
    thumbnail_url: Optional[str] = Field(default=None, alias="thumbnailUrl")
    sort_order: int = Field(default=0, alias="sortOrder")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class GalleryMediaCreateRequest(BaseModel):
    url: str
    type: MediaType = MediaType.IMAGE
    date_time: Optional[str] = Field(default=None, alias="dateTime")
    location: Optional[str] = None
    duration: Optional[str] = None
    audio_url: Optional[str] = Field(default=None, alias="audioUrl")
    description: Optional[str] = None
    thumbnail_url: Optional[str] = Field(default=None, alias="thumbnailUrl")

    class Config:
        populate_by_name = True


class GalleryBase(BaseModel):
    id: str
    family_id: str = Field(alias="familyId")
    name: str
    description: Optional[str] = None
    person_name: Optional[str] = Field(default=None, alias="personName")
    type: GalleryType
    status: GalleryStatus
    progress: int
    cover_url: Optional[str] = Field(default=None, alias="coverUrl")
    media_count: int = Field(default=0, alias="mediaCount")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class GalleryCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    person_name: Optional[str] = Field(default=None, alias="personName")
    type: GalleryType = GalleryType.IMAGE

    class Config:
        populate_by_name = True


class GalleryUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    person_name: Optional[str] = Field(default=None, alias="personName")
    type: Optional[GalleryType] = None
    status: Optional[GalleryStatus] = None
    cover_url: Optional[str] = Field(default=None, alias="coverUrl")

    class Config:
        populate_by_name = True


class GalleryDetailResponse(BaseModel):
    gallery: GalleryBase
    medias: List[GalleryMediaBase]


class GalleryListResponse(BaseModel):
    total: int
    galleries: List[GalleryBase]


class GalleryMediaListResponse(BaseModel):
    total: int
    medias: List[GalleryMediaBase]


class FamilyMemoryType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"


class FamilyMemoryBase(BaseModel):
    id: str
    family_id: str = Field(alias="familyId")
    title: str
    type: FamilyMemoryType
    description: Optional[str] = None
    content: Optional[str] = None
    event_date: Optional[str] = Field(default=None, alias="eventDate")
    location: Optional[str] = None
    media_url: Optional[str] = Field(default=None, alias="mediaUrl")
    media_type: Optional[str] = Field(default=None, alias="mediaType")
    tags: Optional[List[str]] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class FamilyMemoryCreateRequest(BaseModel):
    title: str
    type: FamilyMemoryType = FamilyMemoryType.TEXT
    description: Optional[str] = None
    content: Optional[str] = None
    event_date: Optional[str] = Field(default=None, alias="eventDate")
    location: Optional[str] = None
    media_url: Optional[str] = Field(default=None, alias="mediaUrl")
    media_type: Optional[str] = Field(default=None, alias="mediaType")
    tags: Optional[List[str]] = None
    meta_data: Optional[Dict[str, Any]] = Field(default=None, alias="metadata")

    class Config:
        populate_by_name = True


class FamilyMemoryUpdateRequest(BaseModel):
    title: Optional[str] = None
    type: Optional[FamilyMemoryType] = None
    description: Optional[str] = None
    content: Optional[str] = None
    event_date: Optional[str] = Field(default=None, alias="eventDate")
    location: Optional[str] = None
    media_url: Optional[str] = Field(default=None, alias="mediaUrl")
    media_type: Optional[str] = Field(default=None, alias="mediaType")
    tags: Optional[List[str]] = None
    meta_data: Optional[Dict[str, Any]] = Field(default=None, alias="metadata")

    class Config:
        populate_by_name = True


class FamilyMemoryListResponse(BaseModel):
    total: int
    memories: List[FamilyMemoryBase]


class FamilyMemoryTimelineItem(BaseModel):
    id: str
    title: str
    type: FamilyMemoryType
    description: Optional[str] = None
    event_date: Optional[str] = Field(default=None, alias="eventDate")
    location: Optional[str] = None
    media_url: Optional[str] = Field(default=None, alias="mediaUrl")
    media_type: Optional[str] = Field(default=None, alias="mediaType")
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class FamilyMemoryTimelineResponse(BaseModel):
    total: int
    items: List[FamilyMemoryTimelineItem]


class ImageProcessType(str, enum.Enum):
    RESTORATION = "restoration"
    ENHANCEMENT = "enhancement"
    DYNAMIC_PORTRAIT = "dynamic_portrait"
    CROSS_GENERATION = "cross_generation"
    VIDEO_HIGHLIGHTS = "video_highlights"
    AI_SCENE = "ai_scene"


class ImageProcessStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY_PENDING = "retry_pending"


class ExportFormat(str, enum.Enum):
    JPG = "jpg"
    PNG = "png"
    WEBP = "webp"
    MP4 = "mp4"
    GIF = "gif"


class WatermarkPosition(str, enum.Enum):
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"


class RestorationParams(BaseModel):
    remove_scratches: bool = Field(default=True, alias="removeScratches")
    remove_stains: bool = Field(default=True, alias="removeStains")
    restore_color: bool = Field(default=True, alias="restoreColor")
    sharpen_details: bool = Field(default=True, alias="sharpenDetails")
    denoise_strength: int = Field(default=50, ge=0, le=100, alias="denoiseStrength")
    upscale_factor: int = Field(default=2, ge=1, le=4, alias="upscaleFactor")

    class Config:
        populate_by_name = True


class EnhancementParams(BaseModel):
    upscale_factor: int = Field(default=2, ge=1, le=8, alias="upscaleFactor")
    enhance_face: bool = Field(default=True, alias="enhanceFace")
    sharpen: bool = Field(default=True)
    color_enhance: bool = Field(default=True, alias="colorEnhance")
    hdr_effect: bool = Field(default=False, alias="hdrEffect")

    class Config:
        populate_by_name = True


class DynamicPortraitParams(BaseModel):
    motion_type: str = Field(default="subtle_smile", alias="motionType")
    blink_enabled: bool = Field(default=True, alias="blinkEnabled")
    head_movement: bool = Field(default=True, alias="headMovement")
    duration_seconds: int = Field(default=5, ge=1, le=30, alias="durationSeconds")
    fps: int = Field(default=24, ge=15, le=60)

    class Config:
        populate_by_name = True


class CrossGenerationParams(BaseModel):
    target_age: Optional[int] = Field(default=None, ge=0, le=100, alias="targetAge")
    target_gender: Optional[str] = Field(default=None, alias="targetGender")
    target_style: Optional[str] = Field(default="modern", alias="targetStyle")
    preserve_identity: bool = Field(default=True, alias="preserveIdentity")

    class Config:
        populate_by_name = True


class VideoHighlightsParams(BaseModel):
    highlight_duration: int = Field(default=30, ge=5, le=300, alias="highlightDuration")
    transition_style: str = Field(default="fade", alias="transitionStyle")
    background_music: Optional[str] = Field(default=None, alias="backgroundMusic")
    add_captions: bool = Field(default=False, alias="addCaptions")
    caption_style: Optional[str] = Field(default="elegant", alias="captionStyle")

    class Config:
        populate_by_name = True


class AISceneParams(BaseModel):
    scene_prompt: str = Field(..., alias="scenePrompt")
    style: str = Field(default="photorealistic", alias="style")
    aspect_ratio: str = Field(default="16:9", alias="aspectRatio")
    quality: str = Field(default="high", alias="quality")
    negative_prompt: Optional[str] = Field(default=None, alias="negativePrompt")

    class Config:
        populate_by_name = True


class ExportOptions(BaseModel):
    format: ExportFormat = ExportFormat.JPG
    quality: int = Field(default=90, ge=1, le=100)
    resolution: Optional[str] = Field(default=None)
    add_watermark: bool = Field(default=False, alias="addWatermark")
    watermark_text: Optional[str] = Field(default=None, alias="watermarkText")
    watermark_position: WatermarkPosition = Field(default=WatermarkPosition.BOTTOM_RIGHT, alias="watermarkPosition")

    class Config:
        populate_by_name = True


class CreateProcessTaskRequest(BaseModel):
    gallery_id: str = Field(..., alias="galleryId")
    media_id: Optional[str] = Field(default=None, alias="mediaId")
    media_ids: Optional[List[str]] = Field(default=None, alias="mediaIds")
    task_type: ImageProcessType = Field(..., alias="taskType")
    source_url: Optional[str] = Field(default=None, alias="sourceUrl")

    restoration_params: Optional[RestorationParams] = Field(default=None, alias="restorationParams")
    enhancement_params: Optional[EnhancementParams] = Field(default=None, alias="enhancementParams")
    dynamic_portrait_params: Optional[DynamicPortraitParams] = Field(default=None, alias="dynamicPortraitParams")
    cross_generation_params: Optional[CrossGenerationParams] = Field(default=None, alias="crossGenerationParams")
    video_highlights_params: Optional[VideoHighlightsParams] = Field(default=None, alias="videoHighlightsParams")
    ai_scene_params: Optional[AISceneParams] = Field(default=None, alias="aiSceneParams")

    export_options: Optional[ExportOptions] = Field(default=None, alias="exportOptions")
    callback_url: Optional[str] = Field(default=None, alias="callbackUrl")
    webhook_payload: Optional[Dict[str, Any]] = Field(default=None, alias="webhookPayload")

    class Config:
        populate_by_name = True


class ProcessTaskResponse(BaseModel):
    task_id: str = Field(alias="taskId")
    gallery_id: str = Field(alias="galleryId")
    task_type: ImageProcessType = Field(alias="taskType")
    status: ImageProcessStatus
    progress: int
    message: str

    class Config:
        populate_by_name = True


class ProcessTaskStatusResponse(BaseModel):
    task_id: str = Field(alias="taskId")
    gallery_id: str = Field(alias="galleryId")
    media_id: Optional[str] = Field(default=None, alias="mediaId")
    task_type: ImageProcessType = Field(alias="taskType")
    status: ImageProcessStatus
    progress: int

    source_url: Optional[str] = Field(default=None, alias="sourceUrl")
    result_url: Optional[str] = Field(default=None, alias="resultUrl")
    result_preview_url: Optional[str] = Field(default=None, alias="previewUrl")
    result_metadata: Optional[Dict[str, Any]] = Field(default=None, alias="resultMetadata")

    retry_count: int = Field(alias="retryCount")
    max_retries: int = Field(alias="maxRetries")
    last_error: Optional[str] = Field(default=None, alias="lastError")

    started_at: Optional[datetime] = Field(default=None, alias="startedAt")
    completed_at: Optional[datetime] = Field(default=None, alias="completedAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    estimated_time_remaining: Optional[int] = Field(default=None, alias="estimatedTimeRemaining")
    processing_time: Optional[int] = Field(default=None, alias="processingTime")

    class Config:
        populate_by_name = True
        from_attributes = True


class ProcessTaskListResponse(BaseModel):
    total: int
    tasks: List[ProcessTaskStatusResponse]


class BatchProcessRequest(BaseModel):
    gallery_id: str = Field(..., alias="galleryId")
    media_ids: List[str] = Field(..., alias="mediaIds")
    task_type: ImageProcessType = Field(..., alias="taskType")

    restoration_params: Optional[RestorationParams] = Field(default=None, alias="restorationParams")
    enhancement_params: Optional[EnhancementParams] = Field(default=None, alias="enhancementParams")
    dynamic_portrait_params: Optional[DynamicPortraitParams] = Field(default=None, alias="dynamicPortraitParams")
    cross_generation_params: Optional[CrossGenerationParams] = Field(default=None, alias="crossGenerationParams")
    video_highlights_params: Optional[VideoHighlightsParams] = Field(default=None, alias="videoHighlightsParams")

    export_options: Optional[ExportOptions] = Field(default=None, alias="exportOptions")
    callback_url: Optional[str] = Field(default=None, alias="callbackUrl")

    class Config:
        populate_by_name = True


class BatchProcessResponse(BaseModel):
    total_tasks: int = Field(alias="totalTasks")
    task_ids: List[str] = Field(alias="taskIds")
    message: str

    class Config:
        populate_by_name = True


class RetryTaskRequest(BaseModel):
    reset_retry_count: bool = Field(default=False, alias="resetRetryCount")

    class Config:
        populate_by_name = True


class ProcessResultDownloadRequest(BaseModel):
    task_id: str = Field(..., alias="taskId")
    format: Optional[ExportFormat] = Field(default=None)
    quality: Optional[int] = Field(default=None, ge=1, le=100)

    class Config:
        populate_by_name = True


class ProcessTaskCancelResponse(BaseModel):
    task_id: str = Field(alias="taskId")
    success: bool
    message: str

    class Config:
        populate_by_name = True
