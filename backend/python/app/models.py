from sqlalchemy import (
    Column, String, Integer, Boolean, Text, DateTime, 
    ForeignKey, DECIMAL, Enum as SQLEnum, Index, JSON
)
from sqlalchemy.orm import relationship as orm_relationship
from datetime import datetime
import enum

from app.database import Base, TimestampMixin


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


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('idx_users_username', 'username'),
    )


class AvatarStatus(str, enum.Enum):
    PENDING = "pending"
    GENERATING = "generating"
    TRAINING = "training"
    ACTIVE = "active"
    FAILED = "failed"
    RETRY_PENDING = "retry_pending"


class GenerationMethod(str, enum.Enum):
    PHOTO = "photo"
    TEXT = "text"
    MANUAL = "manual"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY_PENDING = "retry_pending"


class PhotoAngle(str, enum.Enum):
    FRONT = "front"
    LEFT = "left"
    RIGHT = "right"
    BACK = "back"
    CLOSEUP = "closeup"


class MemoryType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    RICHTEXT = "richtext"
    DOCUMENT = "document"


class VoiceMaterialStatus(str, enum.Enum):
    RAW = "raw"
    PREPROCESSING = "preprocessing"
    PREPROCESSED = "preprocessed"


class VoiceModelStatus(str, enum.Enum):
    TRAINING = "training"
    READY = "ready"
    FAILED = "failed"


class SynthesisStatus(str, enum.Enum):
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"


class Avatar(Base, TimestampMixin):
    __tablename__ = "avatars"

    id = Column(String(64), primary_key=True)
    name = Column(String(100), nullable=False)
    relationship = Column(String(50), nullable=False)
    gender = Column(String(10), nullable=False, default="male")
    birth_year = Column(String(10))
    death_year = Column(String(10))
    description = Column(Text)

    generation_method = Column(
        String(20), 
        nullable=False, 
        default="photo"
    )
    text_description = Column(JSON)

    status = Column(
        String(20), 
        nullable=False, 
        default="pending"
    )
    progress = Column(Integer, nullable=False, default=0)

    avatar_url = Column(String(500))
    model_url = Column(String(500))

    fine_tune_adjustments = Column(JSON)
    fine_tuned_at = Column(DateTime(timezone=True))

    voice_model_id = Column(String(64))
    voice_enabled = Column(Boolean, nullable=False, default=False)
    voice_bound_at = Column(DateTime(timezone=True))

    deleted_at = Column(DateTime(timezone=True))

    photos = orm_relationship("Photo", back_populates="avatar", cascade="all, delete-orphan")
    generation_tasks = orm_relationship("GenerationTask", back_populates="avatar", cascade="all, delete-orphan")
    memories = orm_relationship("Memory", back_populates="avatar", cascade="all, delete-orphan")
    voice_materials = orm_relationship("VoiceMaterial", back_populates="avatar", cascade="all, delete-orphan")
    voice_models = orm_relationship("VoiceModel", back_populates="avatar", cascade="all, delete-orphan")
    chat_sessions = orm_relationship("ChatSession", back_populates="avatar", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_avatars_status', 'status'),
        Index('idx_avatars_created_at', 'created_at'),
        Index('idx_avatars_voice_model_id', 'voice_model_id'),
        Index('idx_avatars_deleted_at', 'deleted_at'),
    )


class Photo(Base, TimestampMixin):
    __tablename__ = "photos"

    id = Column(String(64), primary_key=True)
    avatar_id = Column(String(64), ForeignKey('avatars.id', ondelete='CASCADE'), nullable=False)

    photo_data = Column(Text, nullable=False)
    thumbnail = Column(String(500))

    detected_angle = Column(String(20))
    confidence = Column(DECIMAL(5, 4))
    quality_score = Column(Integer)
    features = Column(JSON)

    sort_order = Column(Integer, nullable=False, default=0)

    avatar = orm_relationship("Avatar", back_populates="photos")

    __table_args__ = (
        Index('idx_photos_avatar_id', 'avatar_id'),
        Index('idx_photos_detected_angle', 'detected_angle'),
    )


class GenerationTask(Base, TimestampMixin):
    __tablename__ = "generation_tasks"

    id = Column(String(64), primary_key=True)
    avatar_id = Column(String(64), ForeignKey('avatars.id', ondelete='CASCADE'), nullable=False)

    task_type = Column(String(50), nullable=False, default="avatar_generation")
    status = Column(
        String(20), 
        nullable=False, 
        default="pending"
    )
    progress = Column(Integer, nullable=False, default=0)

    retry_count = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=3)
    last_error = Column(Text)
    failed_at = Column(DateTime(timezone=True))
    next_retry_at = Column(DateTime(timezone=True))

    request_payload = Column(JSON)
    response_payload = Column(JSON)

    external_task_id = Column(String(100))
    external_service = Column(String(100))

    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    avatar = orm_relationship("Avatar", back_populates="generation_tasks")

    __table_args__ = (
        Index('idx_generation_tasks_avatar_id', 'avatar_id'),
        Index('idx_generation_tasks_status', 'status'),
        Index('idx_generation_tasks_external_id', 'external_task_id'),
    )


class Memory(Base, TimestampMixin):
    __tablename__ = "memories"

    id = Column(String(64), primary_key=True)
    avatar_id = Column(String(64), ForeignKey('avatars.id', ondelete='CASCADE'), nullable=False)

    title = Column(String(200), nullable=False)
    type = Column(
        String(20), 
        nullable=False, 
        default="text"
    )
    content = Column(Text, nullable=False)
    description = Column(Text)
    tags = Column(JSON)
    meta_data = Column('meta_data', JSON)

    deleted_at = Column(DateTime(timezone=True))

    avatar = orm_relationship("Avatar", back_populates="memories")

    __table_args__ = (
        Index('idx_memories_avatar_id', 'avatar_id'),
        Index('idx_memories_type', 'type'),
        Index('idx_memories_created_at', 'created_at'),
        Index('idx_memories_deleted_at', 'deleted_at'),
    )


class VoiceMaterial(Base, TimestampMixin):
    __tablename__ = "voice_materials"

    id = Column(String(64), primary_key=True)
    avatar_id = Column(String(64), ForeignKey('avatars.id', ondelete='CASCADE'), nullable=False)

    name = Column(String(200), nullable=False)
    type = Column(String(20), nullable=False, default="upload")
    format = Column(String(20), nullable=False, default="wav")
    duration = Column(Integer)
    size = Column(Integer)

    audio_data = Column(Text)
    audio_url = Column(String(500))

    status = Column(
        String(20), 
        nullable=False, 
        default="raw"
    )
    transcription = Column(Text)
    quality_score = Column(Integer)
    preprocess_info = Column(JSON)

    avatar = orm_relationship("Avatar", back_populates="voice_materials")

    __table_args__ = (
        Index('idx_voice_materials_avatar_id', 'avatar_id'),
        Index('idx_voice_materials_status', 'status'),
    )


class VoiceModel(Base, TimestampMixin):
    __tablename__ = "voice_models"

    id = Column(String(64), primary_key=True)
    avatar_id = Column(String(64), ForeignKey('avatars.id', ondelete='CASCADE'), nullable=False)

    name = Column(String(200), nullable=False)
    status = Column(
        String(20), 
        nullable=False, 
        default="training"
    )
    progress = Column(Integer, nullable=False, default=0)

    material_ids = Column(JSON)
    training_config = Column(JSON)
    quality_metrics = Column(JSON)

    model_path = Column(String(500))
    model_url = Column(String(500))
    sample_audio_path = Column(String(500))
    sample_audio_url = Column(String(500))

    avatar = orm_relationship("Avatar", back_populates="voice_models")

    __table_args__ = (
        Index('idx_voice_models_avatar_id', 'avatar_id'),
        Index('idx_voice_models_status', 'status'),
    )


class VoiceSynthesisTask(Base, TimestampMixin):
    __tablename__ = "voice_synthesis_tasks"

    id = Column(String(64), primary_key=True)
    model_id = Column(String(64), ForeignKey('voice_models.id', ondelete='SET NULL'))
    avatar_id = Column(String(64), ForeignKey('avatars.id', ondelete='CASCADE'), nullable=False)

    text = Column(Text, nullable=False)
    options = Column(JSON)

    status = Column(
        String(20), 
        nullable=False, 
        default="synthesizing"
    )
    progress = Column(Integer, nullable=False, default=0)

    audio_path = Column(String(500))
    audio_url = Column(String(500))
    duration = Column(Integer)

    __table_args__ = (
        Index('idx_voice_synthesis_avatar_id', 'avatar_id'),
        Index('idx_voice_synthesis_model_id', 'model_id'),
        Index('idx_voice_synthesis_status', 'status'),
    )


class ChatSession(Base, TimestampMixin):
    __tablename__ = "chat_sessions"

    id = Column(String(64), primary_key=True)
    avatar_id = Column(String(64), ForeignKey('avatars.id', ondelete='CASCADE'), nullable=False)

    messages = Column(JSON, nullable=False, default=list)

    deleted_at = Column(DateTime(timezone=True))

    avatar = orm_relationship("Avatar", back_populates="chat_sessions")

    __table_args__ = (
        Index('idx_chat_sessions_avatar_id', 'avatar_id'),
        Index('idx_chat_sessions_updated_at', 'updated_at'),
        Index('idx_chat_sessions_deleted_at', 'deleted_at'),
    )


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class MemberStatus(str, enum.Enum):
    ALIVE = "alive"
    DECEASED = "deceased"


class MediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"


class Family(Base, TimestampMixin):
    __tablename__ = "families"

    id = Column(String(64), primary_key=True)
    hall_name = Column(String(100), nullable=True)
    surname = Column(String(50), nullable=False)
    ancestor = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    zi_bei = Column(JSON, nullable=True)

    head_user_id = Column(String(64), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)

    members = orm_relationship("FamilyMember", back_populates="family", cascade="all, delete-orphan")
    head_user = orm_relationship("User", foreign_keys=[head_user_id])

    __table_args__ = (
        Index('idx_families_surname', 'surname'),
        Index('idx_families_head_user_id', 'head_user_id'),
    )


class FamilyMember(Base, TimestampMixin):
    __tablename__ = "family_members"

    id = Column(String(64), primary_key=True)
    family_id = Column(String(64), ForeignKey('families.id', ondelete='CASCADE'), nullable=False)

    name = Column(String(100), nullable=False)
    gender = Column(String(10), nullable=False, default="male")
    generation = Column(Integer, nullable=False, default=1)
    birth_year = Column(String(10), nullable=True)
    death_year = Column(String(10), nullable=True)
    spouse = Column(String(100), nullable=True)
    father_id = Column(String(64), ForeignKey('family_members.id', ondelete='SET NULL'), nullable=True)
    residence = Column(String(200), nullable=True)
    note = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="alive")

    deleted_at = Column(DateTime(timezone=True))

    family = orm_relationship("Family", back_populates="members")
    medias = orm_relationship("MemberMedia", back_populates="member", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_family_members_family_id', 'family_id'),
        Index('idx_family_members_name', 'name'),
        Index('idx_family_members_generation', 'generation'),
        Index('idx_family_members_status', 'status'),
        Index('idx_family_members_father_id', 'father_id'),
        Index('idx_family_members_deleted_at', 'deleted_at'),
    )


class MemberMedia(Base, TimestampMixin):
    __tablename__ = "member_medias"

    id = Column(String(64), primary_key=True)
    member_id = Column(String(64), ForeignKey('family_members.id', ondelete='CASCADE'), nullable=False)

    url = Column(String(500), nullable=False)
    type = Column(String(20), nullable=False, default="image")
    date_time = Column(String(50), nullable=True)
    location = Column(String(200), nullable=True)
    duration = Column(String(20), nullable=True)

    member = orm_relationship("FamilyMember", back_populates="medias")

    __table_args__ = (
        Index('idx_member_medias_member_id', 'member_id'),
        Index('idx_member_medias_type', 'type'),
    )


class FamilyUser(Base, TimestampMixin):
    __tablename__ = "family_users"

    id = Column(String(64), primary_key=True)
    family_id = Column(String(64), ForeignKey('families.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(String(64), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(String(20), nullable=False, default="viewer")

    family = orm_relationship("Family", foreign_keys=[family_id])
    user = orm_relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index('idx_family_users_family_id', 'family_id'),
        Index('idx_family_users_user_id', 'user_id'),
        Index('idx_family_users_role', 'role'),
    )


class FamilyInvitation(Base, TimestampMixin):
    __tablename__ = "family_invitations"

    id = Column(String(64), primary_key=True)
    family_id = Column(String(64), ForeignKey('families.id', ondelete='CASCADE'), nullable=False, index=True)
    inviter_id = Column(String(64), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    invitee_email = Column(String(255), nullable=False)
    invitee_user_id = Column(String(64), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    role = Column(String(20), nullable=False, default="viewer")
    message = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    __table_args__ = (
        Index('idx_family_invitations_family_id', 'family_id'),
        Index('idx_family_invitations_inviter_id', 'inviter_id'),
        Index('idx_family_invitations_invitee_email', 'invitee_email'),
        Index('idx_family_invitations_status', 'status'),
        Index('idx_family_invitations_expires_at', 'expires_at'),
    )


class EditApproval(Base, TimestampMixin):
    __tablename__ = "edit_approvals"

    id = Column(String(64), primary_key=True)
    family_id = Column(String(64), ForeignKey('families.id', ondelete='CASCADE'), nullable=False, index=True)
    requester_id = Column(String(64), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    approver_id = Column(String(64), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    target_type = Column(String(50), nullable=False)
    target_id = Column(String(64), nullable=False)
    operation = Column(String(20), nullable=False)
    original_data = Column(JSON, nullable=True)
    modified_data = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    comment = Column(Text, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    __table_args__ = (
        Index('idx_edit_approvals_family_id', 'family_id'),
        Index('idx_edit_approvals_requester_id', 'requester_id'),
        Index('idx_edit_approvals_approver_id', 'approver_id'),
        Index('idx_edit_approvals_status', 'status'),
        Index('idx_edit_approvals_target', 'target_type', 'target_id'),
    )


class OperationLog(Base, TimestampMixin):
    __tablename__ = "operation_logs"

    id = Column(String(64), primary_key=True)
    family_id = Column(String(64), ForeignKey('families.id', ondelete='SET NULL'), nullable=True, index=True)
    user_id = Column(String(64), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    operation = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=True)
    target_id = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    before_data = Column(JSON, nullable=True)
    after_data = Column(JSON, nullable=True)

    __table_args__ = (
        Index('idx_operation_logs_family_id', 'family_id'),
        Index('idx_operation_logs_user_id', 'user_id'),
        Index('idx_operation_logs_operation', 'operation'),
        Index('idx_operation_logs_created_at', 'created_at'),
    )


class CollaborationLinkStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    USED = "used"
    DISABLED = "disabled"


class CollaborationLink(Base, TimestampMixin):
    __tablename__ = "collaboration_links"

    id = Column(String(64), primary_key=True)
    family_id = Column(String(64), ForeignKey('families.id', ondelete='CASCADE'), nullable=False, index=True)
    inviter_id = Column(String(64), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    link_code = Column(String(32), unique=True, nullable=False, index=True)
    role = Column(String(20), nullable=False, default="viewer")
    status = Column(String(20), nullable=False, default="active")
    is_visible = Column(Boolean, nullable=False, default=True)
    used_count = Column(Integer, nullable=False, default=0)
    max_uses = Column(Integer, nullable=False, default=1)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    used_by_user_id = Column(String(64), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    used_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('idx_collaboration_links_family_id', 'family_id'),
        Index('idx_collaboration_links_inviter_id', 'inviter_id'),
        Index('idx_collaboration_links_link_code', 'link_code'),
        Index('idx_collaboration_links_status', 'status'),
    )


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


class Anniversary(Base, TimestampMixin):
    __tablename__ = "anniversaries"

    id = Column(String(64), primary_key=True)
    family_id = Column(String(64), ForeignKey('families.id', ondelete='CASCADE'), nullable=False, index=True)
    member_id = Column(String(64), ForeignKey('family_members.id', ondelete='CASCADE'), nullable=True, index=True)

    name = Column(String(200), nullable=False)
    type = Column(String(20), nullable=False, default="birthday")
    description = Column(Text, nullable=True)

    date = Column(String(20), nullable=False)
    year = Column(Integer, nullable=True)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)

    repeat_type = Column(String(20), nullable=False, default="yearly")
    is_lunar = Column(Boolean, nullable=False, default=False)

    is_active = Column(Boolean, nullable=False, default=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    family = orm_relationship("Family", foreign_keys=[family_id])
    member = orm_relationship("FamilyMember", foreign_keys=[member_id])

    __table_args__ = (
        Index('idx_anniversaries_family_id', 'family_id'),
        Index('idx_anniversaries_member_id', 'member_id'),
        Index('idx_anniversaries_type', 'type'),
        Index('idx_anniversaries_month_day', 'month', 'day'),
        Index('idx_anniversaries_is_active', 'is_active'),
        Index('idx_anniversaries_deleted_at', 'deleted_at'),
    )


class PushRule(Base, TimestampMixin):
    __tablename__ = "push_rules"

    id = Column(String(64), primary_key=True)
    family_id = Column(String(64), ForeignKey('families.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(String(64), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    anniversary_type = Column(String(20), nullable=True)
    push_channels = Column(JSON, nullable=False, default=list)

    advance_days = Column(Integer, nullable=False, default=0)
    push_time = Column(String(10), nullable=False, default="09:00")

    is_enabled = Column(Boolean, nullable=False, default=True)

    family = orm_relationship("Family", foreign_keys=[family_id])
    user = orm_relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index('idx_push_rules_family_id', 'family_id'),
        Index('idx_push_rules_user_id', 'user_id'),
        Index('idx_push_rules_anniversary_type', 'anniversary_type'),
        Index('idx_push_rules_is_enabled', 'is_enabled'),
    )


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    family_id = Column(String(64), ForeignKey('families.id', ondelete='CASCADE'), nullable=True, index=True)
    anniversary_id = Column(String(64), ForeignKey('anniversaries.id', ondelete='SET NULL'), nullable=True, index=True)

    type = Column(String(30), nullable=False, default="anniversary_reminder")
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)

    status = Column(String(20), nullable=False, default="unread")
    read_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    user = orm_relationship("User", foreign_keys=[user_id])
    family = orm_relationship("Family", foreign_keys=[family_id])
    anniversary = orm_relationship("Anniversary", foreign_keys=[anniversary_id])

    __table_args__ = (
        Index('idx_messages_user_id', 'user_id'),
        Index('idx_messages_family_id', 'family_id'),
        Index('idx_messages_anniversary_id', 'anniversary_id'),
        Index('idx_messages_status', 'status'),
        Index('idx_messages_created_at', 'created_at'),
        Index('idx_messages_deleted_at', 'deleted_at'),
    )


class ScheduledTask(Base, TimestampMixin):
    __tablename__ = "scheduled_tasks"

    id = Column(String(64), primary_key=True)
    task_name = Column(String(100), nullable=False, index=True)
    task_type = Column(String(50), nullable=False)

    anniversary_id = Column(String(64), ForeignKey('anniversaries.id', ondelete='SET NULL'), nullable=True, index=True)
    user_id = Column(String(64), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)

    scheduled_time = Column(DateTime(timezone=True), nullable=False, index=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)

    status = Column(String(20), nullable=False, default="pending")
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    retry_count = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=3)

    anniversary = orm_relationship("Anniversary", foreign_keys=[anniversary_id])
    user = orm_relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index('idx_scheduled_tasks_task_name', 'task_name'),
        Index('idx_scheduled_tasks_task_type', 'task_type'),
        Index('idx_scheduled_tasks_anniversary_id', 'anniversary_id'),
        Index('idx_scheduled_tasks_user_id', 'user_id'),
        Index('idx_scheduled_tasks_scheduled_time', 'scheduled_time'),
        Index('idx_scheduled_tasks_status', 'status'),
    )


class GalleryStatus(str, enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"


class GalleryType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"


class Gallery(Base, TimestampMixin):
    __tablename__ = "galleries"

    id = Column(String(64), primary_key=True)
    family_id = Column(String(64), ForeignKey('families.id', ondelete='CASCADE'), nullable=False, index=True)

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    person_name = Column(String(100), nullable=True)
    type = Column(String(20), nullable=False, default="image")
    status = Column(String(20), nullable=False, default="draft")
    progress = Column(Integer, nullable=False, default=0)

    cover_url = Column(String(500), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    medias = orm_relationship("GalleryMedia", back_populates="gallery", cascade="all, delete-orphan")
    family = orm_relationship("Family", foreign_keys=[family_id])

    __table_args__ = (
        Index('idx_galleries_family_id', 'family_id'),
        Index('idx_galleries_status', 'status'),
        Index('idx_galleries_created_at', 'created_at'),
        Index('idx_galleries_deleted_at', 'deleted_at'),
    )


class GalleryMedia(Base, TimestampMixin):
    __tablename__ = "gallery_medias"

    id = Column(String(64), primary_key=True)
    gallery_id = Column(String(64), ForeignKey('galleries.id', ondelete='CASCADE'), nullable=False, index=True)

    url = Column(String(500), nullable=False)
    type = Column(String(20), nullable=False, default="image")
    date_time = Column(String(50), nullable=True)
    location = Column(String(200), nullable=True)
    duration = Column(String(20), nullable=True)
    audio_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)

    thumbnail_url = Column(String(500), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)

    gallery = orm_relationship("Gallery", back_populates="medias")

    __table_args__ = (
        Index('idx_gallery_medias_gallery_id', 'gallery_id'),
        Index('idx_gallery_medias_type', 'type'),
        Index('idx_gallery_medias_created_at', 'created_at'),
    )
