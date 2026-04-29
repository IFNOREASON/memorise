from sqlalchemy import (
    Column, String, Integer, Boolean, Text, DateTime, 
    ForeignKey, DECIMAL, Enum as SQLEnum, Index, JSON
)
from sqlalchemy.orm import relationship as orm_relationship
from datetime import datetime
import enum

from app.database import Base, TimestampMixin


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
