import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from sqlalchemy import text
from app.database import AsyncSessionLocal
from app.models import Base

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS image_process_tasks (
    id VARCHAR(64) PRIMARY KEY,
    gallery_id VARCHAR(64) NOT NULL REFERENCES galleries(id) ON DELETE CASCADE,
    media_id VARCHAR(64) REFERENCES gallery_medias(id) ON DELETE SET NULL,
    family_id VARCHAR(64) NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    task_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    progress INTEGER NOT NULL DEFAULT 0,
    source_url VARCHAR(500),
    source_media_ids JSONB,
    result_url VARCHAR(500),
    result_preview_url VARCHAR(500),
    result_metadata JSONB,
    parameters JSONB,
    options JSONB,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    last_error TEXT,
    failed_at TIMESTAMP WITH TIME ZONE,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    external_task_id VARCHAR(100),
    external_service VARCHAR(100),
    callback_url VARCHAR(500),
    webhook_payload JSONB,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    watermark_text VARCHAR(200),
    watermark_position VARCHAR(50),
    export_format VARCHAR(20),
    export_quality INTEGER DEFAULT 90,
    size_info JSONB,
    processing_time INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_image_process_tasks_status ON image_process_tasks(status);
CREATE INDEX IF NOT EXISTS idx_image_process_tasks_task_type ON image_process_tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_image_process_tasks_gallery_id ON image_process_tasks(gallery_id);
CREATE INDEX IF NOT EXISTS idx_image_process_tasks_family_id ON image_process_tasks(family_id);
CREATE INDEX IF NOT EXISTS idx_image_process_tasks_created_at ON image_process_tasks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_image_process_tasks_external_id ON image_process_tasks(external_task_id);
"""


async def migrate():
    print("开始迁移：添加AI影像处理任务表...")
    
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(text(CREATE_TABLE_SQL))
            await db.commit()
            print("✅ image_process_tasks 表创建成功")
            
            result = await db.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'image_process_tasks'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            print(f"\n表结构 ({len(columns)} 列):")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
            
            result = await db.execute(text("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'image_process_tasks'
            """))
            indexes = result.fetchall()
            print(f"\n索引 ({len(indexes)} 个):")
            for idx in indexes:
                print(f"  - {idx[0]}")
            
            print("\n✅ 迁移完成！")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ 迁移失败: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(migrate())
