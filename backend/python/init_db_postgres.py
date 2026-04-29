"""
PostgreSQL 数据库初始化脚本
密码: 123456

此脚本会：
1. 连接到 PostgreSQL 默认数据库 (postgres)
2. 创建 memorise 数据库（如果不存在）
3. 然后启动后端服务器时，SQLAlchemy 会自动创建所有表
"""

import asyncio
import sys

try:
    import asyncpg
except ImportError:
    print("错误: 请先安装 asyncpg 库")
    print("运行: pip install asyncpg")
    sys.exit(1)

from app.config import settings


async def create_database_if_not_exists():
    """创建 memorise 数据库（如果不存在）"""
    
    # 解析数据库连接字符串
    # 格式: postgresql+asyncpg://postgres:123456@localhost:5432/memorise
    db_url = settings.DATABASE_URL
    
    # 移除驱动前缀
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    # 提取连接信息
    # postgresql://postgres:123456@localhost:5432/memorise
    parts = db_url.split("//")[1].split("@")
    user_pass = parts[0].split(":")
    host_db = parts[1].split("/")
    
    user = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ""
    host_port = host_db[0].split(":")
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 5432
    target_db = host_db[1] if len(host_db) > 1 else "memorise"
    
    print("=" * 60)
    print("PostgreSQL 数据库初始化")
    print("=" * 60)
    print(f"主机: {host}")
    print(f"端口: {port}")
    print(f"用户: {user}")
    print(f"目标数据库: {target_db}")
    print("=" * 60)
    
    # 连接到默认的 postgres 数据库
    try:
        print(f"\n正在连接到 PostgreSQL 默认数据库 (postgres)...")
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"
        )
        
        # 检查目标数据库是否存在
        result = await conn.fetchrow(
            "SELECT 1 FROM pg_database WHERE datname = $1", target_db
        )
        
        if not result:
            print(f"数据库 '{target_db}' 不存在，正在创建...")
            # 创建数据库
            await conn.execute(f'CREATE DATABASE "{target_db}"')
            print(f"✅ 数据库 '{target_db}' 创建成功")
        else:
            print(f"✅ 数据库 '{target_db}' 已存在")
        
        await conn.close()
        
        # 现在连接到目标数据库，测试连接
        print(f"\n正在测试连接到 '{target_db}' 数据库...")
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=target_db
        )
        
        print("✅ 数据库连接成功")
        
        # 检查是否有 users 表（用于确认表是否已创建）
        try:
            result = await conn.fetchrow(
                "SELECT 1 FROM information_schema.tables WHERE table_name = 'users'"
            )
            if result:
                print("✅ 表结构已存在")
            else:
                print("ℹ️  表结构将在后端启动时自动创建")
        except Exception as e:
            print(f"⚠️  检查表时出错: {e}")
        
        await conn.close()
        
        print("\n" + "=" * 60)
        print("数据库初始化完成！")
        print("=" * 60)
        print("\n下一步：启动后端服务器")
        print("命令: python start_server.py")
        print("\n后端启动后，SQLAlchemy 会自动创建所有表")
        
        return True
        
    except asyncpg.exceptions.PostgresError as e:
        print(f"\n❌ PostgreSQL 错误: {e}")
        print("\n可能的原因：")
        print("1. PostgreSQL 服务未启动")
        print("2. 密码错误（当前密码: 123456）")
        print("3. 用户名错误（当前用户名: postgres）")
        print("4. PostgreSQL 端口不是 5432")
        return False
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return False


async def main():
    success = await create_database_if_not_exists()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
