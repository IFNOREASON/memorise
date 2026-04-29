import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

DATABASE_URL = 'postgresql+asyncpg://postgres:123456@localhost:5432/memorise'

async def check_data():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(text("SELECT id, name, voice_model_id FROM avatars WHERE deleted_at IS NULL"))
        avatars = result.fetchall()
        print('=== 数字人列表 ===')
        for row in avatars:
            print(f'  ID: {row[0]}, 名称: {row[1]}, 语音模型ID: {row[2]}')
        
        result = await session.execute(text("SELECT id, avatar_id, name, status, duration, audio_url FROM voice_materials"))
        materials = result.fetchall()
        print('\n=== 声音素材列表 ===')
        for row in materials:
            print(f'  ID: {row[0]}, AvatarID: {row[1]}, 名称: {row[2]}, 状态: {row[3]}, 时长: {row[4]}秒, URL: {row[5]}')
        
        result = await session.execute(text("SELECT id, avatar_id, name, status, progress, model_url FROM voice_models"))
        models = result.fetchall()
        print('\n=== 声音模型列表 ===')
        for row in models:
            print(f'  ID: {row[0]}, AvatarID: {row[1]}, 名称: {row[2]}, 状态: {row[3]}, 进度: {row[4]}%, 模型URL: {row[5]}')
    
    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(check_data())
