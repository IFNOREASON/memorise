import asyncio
from sqlalchemy import text, Column, String, ForeignKey, Index
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings
from app.models import Family


async def migrate():
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
        pool_pre_ping=True,
    )

    async with engine.begin() as conn:
        print("开始迁移: 为 families 表添加 head_user_id 字段...")
        
        try:
            result = await conn.execute(text(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'families' 
                AND column_name = 'head_user_id'
                """
            ))
            column_exists = result.scalar_one_or_none()
            
            if column_exists:
                print("head_user_id 字段已存在，跳过迁移")
            else:
                print("添加 head_user_id 字段...")
                await conn.execute(text(
                    """
                    ALTER TABLE families 
                    ADD COLUMN head_user_id VARCHAR(64)
                    """
                ))
                print("字段添加成功")
            
        except Exception as e:
            print(f"添加字段时出错: {e}")
            print("尝试继续添加索引...")
        
        try:
            result = await conn.execute(text(
                """
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'families' 
                AND indexname = 'idx_families_head_user_id'
                """
            ))
            index_exists = result.scalar_one_or_none()
            
            if index_exists:
                print("idx_families_head_user_id 索引已存在，跳过")
            else:
                print("添加 idx_families_head_user_id 索引...")
                await conn.execute(text(
                    """
                    CREATE INDEX idx_families_head_user_id 
                    ON families (head_user_id)
                    """
                ))
                print("索引添加成功")
                
        except Exception as e:
            print(f"添加索引时出错: {e}")
        
        try:
            result = await conn.execute(text(
                """
                SELECT conname 
                FROM pg_constraint 
                WHERE conname = 'fk_families_head_user'
                """
            ))
            fk_exists = result.scalar_one_or_none()
            
            if fk_exists:
                print("外键约束已存在，跳过")
            else:
                print("添加外键约束...")
                await conn.execute(text(
                    """
                    ALTER TABLE families 
                    ADD CONSTRAINT fk_families_head_user 
                    FOREIGN KEY (head_user_id) 
                    REFERENCES users (id) 
                    ON DELETE SET NULL
                    """
                ))
                print("外键约束添加成功")
                
        except Exception as e:
            print(f"添加外键约束时出错: {e}")
        
        print("\n迁移完成!")
        
        print("\n正在更新现有数据: 将 family_users 中的 head 角色同步到 families.head_user_id...")
        try:
            update_result = await conn.execute(text(
                """
                UPDATE families f
                SET head_user_id = fu.user_id
                FROM family_users fu
                WHERE f.id = fu.family_id
                AND fu.role = 'head'
                AND f.head_user_id IS NULL
                """
            ))
            print(f"已更新 {update_result.rowcount} 条记录")
        except Exception as e:
            print(f"更新数据时出错: {e}")

    await engine.dispose()
    print("\n迁移脚本执行完成")


if __name__ == "__main__":
    asyncio.run(migrate())
