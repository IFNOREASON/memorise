-- ============================================
-- Memorise 数字人系统 PostgreSQL 数据库初始化脚本
-- 创建时间: 2026-04-28
-- ============================================

-- 创建数据库（如果不存在）
-- 注意：需要在连接到默认数据库（如postgres）时执行此语句
-- CREATE DATABASE memorise WITH ENCODING 'UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8';

-- 连接到memorise数据库后执行以下脚本

-- 创建枚举类型
CREATE TYPE avatar_status AS ENUM (
    'pending',
    'generating',
    'training',
    'active',
    'failed',
    'retry_pending'
);

CREATE TYPE generation_method AS ENUM (
    'photo',
    'text',
    'manual'
);

CREATE TYPE task_status AS ENUM (
    'pending',
    'processing',
    'completed',
    'failed',
    'retry_pending'
);

CREATE TYPE photo_angle AS ENUM (
    'front',
    'left',
    'right',
    'back',
    'closeup'
);

CREATE TYPE memory_type AS ENUM (
    'text',
    'image',
    'video',
    'richtext',
    'document'
);

CREATE TYPE voice_material_status AS ENUM (
    'raw',
    'preprocessing',
    'preprocessed'
);

CREATE TYPE voice_model_status AS ENUM (
    'training',
    'ready',
    'failed'
);

CREATE TYPE synthesis_status AS ENUM (
    'synthesizing',
    'completed',
    'failed'
);

-- 创建扩展（用于UUID生成）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 核心表结构
-- ============================================

-- 数字人表
CREATE TABLE avatars (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'avatar_' || to_char(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISSMS') || '_' || substring(md5(random()::text), 1, 6),
    name VARCHAR(100) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    gender VARCHAR(10) NOT NULL DEFAULT 'male',
    birth_year VARCHAR(10),
    death_year VARCHAR(10),
    description TEXT,
    
    generation_method generation_method NOT NULL DEFAULT 'photo',
    text_description JSONB,
    
    status avatar_status NOT NULL DEFAULT 'pending',
    progress INTEGER NOT NULL DEFAULT 0,
    
    avatar_url VARCHAR(500),
    model_url VARCHAR(500),
    
    fine_tune_adjustments JSONB,
    fine_tuned_at TIMESTAMP,
    
    voice_model_id VARCHAR(64),
    voice_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    voice_bound_at TIMESTAMP,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 照片表（存储五视图照片）
CREATE TABLE photos (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'photo_' || to_char(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISSMS') || '_' || substring(md5(random()::text), 1, 6),
    avatar_id VARCHAR(64) NOT NULL REFERENCES avatars(id) ON DELETE CASCADE,
    
    photo_data TEXT NOT NULL,
    thumbnail VARCHAR(500),
    
    detected_angle photo_angle,
    confidence DECIMAL(5, 4),
    quality_score INTEGER,
    features JSONB,
    
    sort_order INTEGER NOT NULL DEFAULT 0,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 生成任务表（支持失败重试机制）
CREATE TABLE generation_tasks (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'task_' || to_char(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISSMS') || '_' || substring(md5(random()::text), 1, 6),
    avatar_id VARCHAR(64) NOT NULL REFERENCES avatars(id) ON DELETE CASCADE,
    
    task_type VARCHAR(50) NOT NULL DEFAULT 'avatar_generation',
    status task_status NOT NULL DEFAULT 'pending',
    progress INTEGER NOT NULL DEFAULT 0,
    
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    last_error TEXT,
    failed_at TIMESTAMP,
    next_retry_at TIMESTAMP,
    
    request_payload JSONB,
    response_payload JSONB,
    
    external_task_id VARCHAR(100),
    external_service VARCHAR(100),
    
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 记忆表
CREATE TABLE memories (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'memory_' || to_char(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISSMS') || '_' || substring(md5(random()::text), 1, 6),
    avatar_id VARCHAR(64) NOT NULL REFERENCES avatars(id) ON DELETE CASCADE,
    
    title VARCHAR(200) NOT NULL,
    type memory_type NOT NULL DEFAULT 'text',
    content TEXT NOT NULL,
    description TEXT,
    tags JSONB,
    meta_data JSONB,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 声音素材表
CREATE TABLE voice_materials (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'voice_material_' || to_char(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISSMS') || '_' || substring(md5(random()::text), 1, 6),
    avatar_id VARCHAR(64) NOT NULL REFERENCES avatars(id) ON DELETE CASCADE,
    
    name VARCHAR(200) NOT NULL,
    type VARCHAR(20) NOT NULL DEFAULT 'upload',
    format VARCHAR(20) NOT NULL DEFAULT 'wav',
    duration INTEGER,
    size BIGINT,
    
    audio_data TEXT,
    audio_url VARCHAR(500),
    
    status voice_material_status NOT NULL DEFAULT 'raw',
    transcription TEXT,
    quality_score INTEGER,
    preprocess_info JSONB,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 声音模型表
CREATE TABLE voice_models (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'voice_model_' || to_char(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISSMS') || '_' || substring(md5(random()::text), 1, 6),
    avatar_id VARCHAR(64) NOT NULL REFERENCES avatars(id) ON DELETE CASCADE,
    
    name VARCHAR(200) NOT NULL,
    status voice_model_status NOT NULL DEFAULT 'training',
    progress INTEGER NOT NULL DEFAULT 0,
    
    material_ids JSONB,
    training_config JSONB,
    quality_metrics JSONB,
    
    model_path VARCHAR(500),
    model_url VARCHAR(500),
    sample_audio_path VARCHAR(500),
    sample_audio_url VARCHAR(500),
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 语音合成任务表
CREATE TABLE voice_synthesis_tasks (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'voice_synth_' || to_char(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISSMS') || '_' || substring(md5(random()::text), 1, 6),
    model_id VARCHAR(64) REFERENCES voice_models(id) ON DELETE SET NULL,
    avatar_id VARCHAR(64) NOT NULL REFERENCES avatars(id) ON DELETE CASCADE,
    
    text TEXT NOT NULL,
    options JSONB,
    
    status synthesis_status NOT NULL DEFAULT 'synthesizing',
    progress INTEGER NOT NULL DEFAULT 0,
    
    audio_path VARCHAR(500),
    audio_url VARCHAR(500),
    duration INTEGER,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 对话会话表
CREATE TABLE chat_sessions (
    id VARCHAR(64) PRIMARY KEY DEFAULT 'chat_session_' || to_char(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISSMS') || '_' || substring(md5(random()::text), 1, 6),
    avatar_id VARCHAR(64) NOT NULL REFERENCES avatars(id) ON DELETE CASCADE,
    
    messages JSONB NOT NULL DEFAULT '[]'::jsonb,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- ============================================
-- 索引创建
-- ============================================

-- avatars 表索引
CREATE INDEX idx_avatars_status ON avatars(status);
CREATE INDEX idx_avatars_created_at ON avatars(created_at);
CREATE INDEX idx_avatars_voice_model_id ON avatars(voice_model_id);
CREATE INDEX idx_avatars_deleted_at ON avatars(deleted_at);

-- photos 表索引
CREATE INDEX idx_photos_avatar_id ON photos(avatar_id);
CREATE INDEX idx_photos_detected_angle ON photos(detected_angle);
CREATE INDEX idx_photos_sort_order ON photos(avatar_id, sort_order);

-- generation_tasks 表索引
CREATE INDEX idx_generation_tasks_avatar_id ON generation_tasks(avatar_id);
CREATE INDEX idx_generation_tasks_status ON generation_tasks(status);
CREATE INDEX idx_generation_tasks_next_retry ON generation_tasks(next_retry_at) WHERE status = 'retry_pending';
CREATE INDEX idx_generation_tasks_external_id ON generation_tasks(external_task_id);

-- memories 表索引
CREATE INDEX idx_memories_avatar_id ON memories(avatar_id);
CREATE INDEX idx_memories_type ON memories(type);
CREATE INDEX idx_memories_created_at ON memories(created_at);
CREATE INDEX idx_memories_deleted_at ON memories(deleted_at);

-- voice_materials 表索引
CREATE INDEX idx_voice_materials_avatar_id ON voice_materials(avatar_id);
CREATE INDEX idx_voice_materials_status ON voice_materials(status);

-- voice_models 表索引
CREATE INDEX idx_voice_models_avatar_id ON voice_models(avatar_id);
CREATE INDEX idx_voice_models_status ON voice_models(status);

-- voice_synthesis_tasks 表索引
CREATE INDEX idx_voice_synthesis_avatar_id ON voice_synthesis_tasks(avatar_id);
CREATE INDEX idx_voice_synthesis_model_id ON voice_synthesis_tasks(model_id);
CREATE INDEX idx_voice_synthesis_status ON voice_synthesis_tasks(status);

-- chat_sessions 表索引
CREATE INDEX idx_chat_sessions_avatar_id ON chat_sessions(avatar_id);
CREATE INDEX idx_chat_sessions_updated_at ON chat_sessions(updated_at);
CREATE INDEX idx_chat_sessions_deleted_at ON chat_sessions(deleted_at);

-- ============================================
-- 触发器和函数
-- ============================================

-- 更新时间戳触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有有 updated_at 字段的表创建触发器
CREATE TRIGGER update_avatars_updated_at BEFORE UPDATE ON avatars
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_photos_updated_at BEFORE UPDATE ON photos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_generation_tasks_updated_at BEFORE UPDATE ON generation_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_memories_updated_at BEFORE UPDATE ON memories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_voice_materials_updated_at BEFORE UPDATE ON voice_materials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_voice_models_updated_at BEFORE UPDATE ON voice_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_voice_synthesis_tasks_updated_at BEFORE UPDATE ON voice_synthesis_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 任务重试调度函数
-- ============================================

-- 计算下次重试时间（指数退避）
CREATE OR REPLACE FUNCTION calculate_next_retry_time(
    p_retry_count INTEGER
) RETURNS TIMESTAMP AS $$
DECLARE
    v_delay_seconds INTEGER;
BEGIN
    v_delay_seconds := CASE 
        WHEN p_retry_count = 0 THEN 60
        WHEN p_retry_count = 1 THEN 120
        WHEN p_retry_count = 2 THEN 300
        ELSE 600
    END;
    RETURN CURRENT_TIMESTAMP + (v_delay_seconds || ' seconds')::INTERVAL;
END;
$$ language 'plpgsql';

-- ============================================
-- 注释
-- ============================================

COMMENT ON TABLE avatars IS '数字人主表';
COMMENT ON COLUMN avatars.status IS '状态: pending(待处理), generating(生成中), training(训练中), active(已激活), failed(失败), retry_pending(待重试)';
COMMENT ON COLUMN avatars.retry_count IS '重试次数';

COMMENT ON TABLE photos IS '照片表，存储五视图照片';
COMMENT ON COLUMN photos.detected_angle IS '检测到的角度: front(正面), left(左侧), right(右侧), back(背面), closeup(特写)';

COMMENT ON TABLE generation_tasks IS '生成任务表，支持失败重试机制';
COMMENT ON COLUMN generation_tasks.retry_count IS '已重试次数';
COMMENT ON COLUMN generation_tasks.max_retries IS '最大重试次数';
COMMENT ON COLUMN generation_tasks.next_retry_at IS '下次重试时间';
COMMENT ON COLUMN generation_tasks.last_error IS '上次错误信息';

COMMENT ON TABLE memories IS '记忆表';
COMMENT ON TABLE voice_materials IS '声音素材表';
COMMENT ON TABLE voice_models IS '声音模型表';
COMMENT ON TABLE voice_synthesis_tasks IS '语音合成任务表';
COMMENT ON TABLE chat_sessions IS '对话会话表';
