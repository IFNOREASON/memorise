-- ============================================================
-- Memorise 数据库初始化脚本 (PostgreSQL)
-- ============================================================
-- 数据库密码: 123456
-- ============================================================

-- 1. 创建数据库（如果不存在）
-- 注意：需要以超级用户身份执行此部分
-- CREATE DATABASE memorise
--     WITH 
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'Chinese_PRC.UTF8'
--     LC_CTYPE = 'Chinese_PRC.UTF8'
--     CONNECTION LIMIT = -1;

-- 2. 连接到 memorise 数据库后执行以下脚本

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 用户表 (users)
-- ============================================================
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id VARCHAR(64) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    avatar_url VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);

COMMENT ON TABLE users IS '用户表';
COMMENT ON COLUMN users.id IS '用户唯一标识';
COMMENT ON COLUMN users.username IS '用户名（用于登录）';
COMMENT ON COLUMN users.password_hash IS '密码哈希（PBKDF2-SHA256 加密）';
COMMENT ON COLUMN users.nickname IS '昵称';
COMMENT ON COLUMN users.avatar_url IS '头像 URL';
COMMENT ON COLUMN users.is_active IS '是否激活';
COMMENT ON COLUMN users.last_login_at IS '最后登录时间';
COMMENT ON COLUMN users.created_at IS '创建时间';
COMMENT ON COLUMN users.updated_at IS '更新时间';

-- ============================================================
-- 数字人表 (avatars)
-- ============================================================
DROP TABLE IF EXISTS avatars CASCADE;

CREATE TABLE avatars (
    id VARCHAR(64) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    name VARCHAR(100) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    gender VARCHAR(10) NOT NULL DEFAULT 'male',
    birth_year VARCHAR(10),
    death_year VARCHAR(10),
    description TEXT,
    generation_method VARCHAR(20) NOT NULL DEFAULT 'photo',
    text_description JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    progress INTEGER NOT NULL DEFAULT 0,
    avatar_url VARCHAR(500),
    model_url VARCHAR(500),
    fine_tune_adjustments JSONB,
    fine_tuned_at TIMESTAMP WITH TIME ZONE,
    voice_model_id VARCHAR(64),
    voice_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    voice_bound_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_avatars_status ON avatars(status);
CREATE INDEX idx_avatars_created_at ON avatars(created_at);
CREATE INDEX idx_avatars_voice_model_id ON avatars(voice_model_id);
CREATE INDEX idx_avatars_deleted_at ON avatars(deleted_at);

-- ============================================================
-- 照片表 (photos)
-- ============================================================
DROP TABLE IF EXISTS photos CASCADE;

CREATE TABLE photos (
    id VARCHAR(64) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    avatar_id VARCHAR(64) NOT NULL,
    photo_data TEXT NOT NULL,
    thumbnail VARCHAR(500),
    detected_angle VARCHAR(20),
    confidence DECIMAL(5,4),
    quality_score INTEGER,
    features JSONB,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (avatar_id) REFERENCES avatars(id) ON DELETE CASCADE
);

CREATE INDEX idx_photos_avatar_id ON photos(avatar_id);
CREATE INDEX idx_photos_detected_angle ON photos(detected_angle);

-- ============================================================
-- 生成任务表 (generation_tasks)
-- ============================================================
DROP TABLE IF EXISTS generation_tasks CASCADE;

CREATE TABLE generation_tasks (
    id VARCHAR(64) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    avatar_id VARCHAR(64) NOT NULL,
    task_type VARCHAR(50) NOT NULL DEFAULT 'avatar_generation',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    progress INTEGER NOT NULL DEFAULT 0,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    last_error TEXT,
    failed_at TIMESTAMP WITH TIME ZONE,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    request_payload JSONB,
    response_payload JSONB,
    external_task_id VARCHAR(100),
    external_service VARCHAR(100),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (avatar_id) REFERENCES avatars(id) ON DELETE CASCADE
);

CREATE INDEX idx_generation_tasks_avatar_id ON generation_tasks(avatar_id);
CREATE INDEX idx_generation_tasks_status ON generation_tasks(status);
CREATE INDEX idx_generation_tasks_external_id ON generation_tasks(external_task_id);

-- ============================================================
-- 记忆表 (memories)
-- ============================================================
DROP TABLE IF EXISTS memories CASCADE;

CREATE TABLE memories (
    id VARCHAR(64) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    avatar_id VARCHAR(64) NOT NULL,
    title VARCHAR(200) NOT NULL,
    type VARCHAR(20) NOT NULL DEFAULT 'text',
    content TEXT NOT NULL,
    description TEXT,
    tags JSONB,
    meta_data JSONB,
    deleted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (avatar_id) REFERENCES avatars(id) ON DELETE CASCADE
);

CREATE INDEX idx_memories_avatar_id ON memories(avatar_id);
CREATE INDEX idx_memories_type ON memories(type);
CREATE INDEX idx_memories_created_at ON memories(created_at);
CREATE INDEX idx_memories_deleted_at ON memories(deleted_at);

-- ============================================================
-- 语音素材表 (voice_materials)
-- ============================================================
DROP TABLE IF EXISTS voice_materials CASCADE;

CREATE TABLE voice_materials (
    id VARCHAR(64) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    avatar_id VARCHAR(64) NOT NULL,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(20) NOT NULL DEFAULT 'upload',
    format VARCHAR(20) NOT NULL DEFAULT 'wav',
    duration INTEGER,
    size INTEGER,
    audio_data TEXT,
    audio_url VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT 'raw',
    transcription TEXT,
    quality_score INTEGER,
    preprocess_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (avatar_id) REFERENCES avatars(id) ON DELETE CASCADE
);

CREATE INDEX idx_voice_materials_avatar_id ON voice_materials(avatar_id);
CREATE INDEX idx_voice_materials_status ON voice_materials(status);

-- ============================================================
-- 语音模型表 (voice_models)
-- ============================================================
DROP TABLE IF EXISTS voice_models CASCADE;

CREATE TABLE voice_models (
    id VARCHAR(64) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    avatar_id VARCHAR(64) NOT NULL,
    name VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'training',
    progress INTEGER NOT NULL DEFAULT 0,
    material_ids JSONB,
    training_config JSONB,
    quality_metrics JSONB,
    model_path VARCHAR(500),
    model_url VARCHAR(500),
    sample_audio_path VARCHAR(500),
    sample_audio_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (avatar_id) REFERENCES avatars(id) ON DELETE CASCADE
);

CREATE INDEX idx_voice_models_avatar_id ON voice_models(avatar_id);
CREATE INDEX idx_voice_models_status ON voice_models(status);

-- ============================================================
-- 语音合成任务表 (voice_synthesis_tasks)
-- ============================================================
DROP TABLE IF EXISTS voice_synthesis_tasks CASCADE;

CREATE TABLE voice_synthesis_tasks (
    id VARCHAR(64) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    model_id VARCHAR(64),
    avatar_id VARCHAR(64) NOT NULL,
    text TEXT NOT NULL,
    options JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'synthesizing',
    progress INTEGER NOT NULL DEFAULT 0,
    audio_path VARCHAR(500),
    audio_url VARCHAR(500),
    duration INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES voice_models(id) ON DELETE SET NULL,
    FOREIGN KEY (avatar_id) REFERENCES avatars(id) ON DELETE CASCADE
);

CREATE INDEX idx_voice_synthesis_avatar_id ON voice_synthesis_tasks(avatar_id);
CREATE INDEX idx_voice_synthesis_model_id ON voice_synthesis_tasks(model_id);
CREATE INDEX idx_voice_synthesis_status ON voice_synthesis_tasks(status);

-- ============================================================
-- 聊天会话表 (chat_sessions)
-- ============================================================
DROP TABLE IF EXISTS chat_sessions CASCADE;

CREATE TABLE chat_sessions (
    id VARCHAR(64) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    avatar_id VARCHAR(64) NOT NULL,
    messages JSONB NOT NULL DEFAULT '[]'::jsonb,
    deleted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (avatar_id) REFERENCES avatars(id) ON DELETE CASCADE
);

CREATE INDEX idx_chat_sessions_avatar_id ON chat_sessions(avatar_id);
CREATE INDEX idx_chat_sessions_updated_at ON chat_sessions(updated_at);
CREATE INDEX idx_chat_sessions_deleted_at ON chat_sessions(deleted_at);

-- ============================================================
-- 创建更新时间触发器函数
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================================
-- 为所有表创建更新时间触发器
-- ============================================================
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

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

-- ============================================================
-- 插入测试数据（可选）
-- ============================================================
-- 注意：密码使用 PBKDF2-SHA256 加密
-- 示例：密码 '123456' 的加密格式为：
-- pbkdf2_sha256$100000$<salt>$<hash>

-- INSERT INTO users (id, username, password_hash, nickname, is_active)
-- VALUES (
--     '00000000-0000-0000-0000-000000000001',
--     'admin',
--     'pbkdf2_sha256$100000$example_salt$example_hash',
--     '管理员',
--     TRUE
-- );

-- ============================================================
-- 完成
-- ============================================================
COMMENT ON DATABASE memorise IS 'Memorise 数字人记忆管理系统数据库';

-- 显示创建的表
\dt
