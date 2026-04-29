"""
PostgreSQL 数据库初始化脚本（简化版）
密码: 123456
"""

import asyncio
import sys

try:
    import asyncpg
except ImportError:
    print("Error: Please install asyncpg first")
    print("Run: pip install asyncpg")
    sys.exit(1)

from app.config import settings


async def check_and_create_database():
    db_url = settings.DATABASE_URL
    
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    
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
    print("PostgreSQL Database Initialization")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"User: {user}")
    print(f"Target Database: {target_db}")
    print("=" * 60)
    
    try:
        print(f"\nConnecting to PostgreSQL default database (postgres)...")
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"
        )
        
        result = await conn.fetchrow(
            "SELECT 1 FROM pg_database WHERE datname = $1", target_db
        )
        
        if not result:
            print(f"Database '{target_db}' does not exist, creating...")
            await conn.execute(f'CREATE DATABASE "{target_db}"')
            print(f"Database '{target_db}' created successfully")
        else:
            print(f"Database '{target_db}' already exists")
        
        await conn.close()
        
        print(f"\nTesting connection to '{target_db}' database...")
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=target_db
        )
        
        print("Database connection successful")
        
        try:
            result = await conn.fetchrow(
                "SELECT 1 FROM information_schema.tables WHERE table_name = 'users'"
            )
            if result:
                print("Tables already exist")
            else:
                print("Tables will be created automatically when backend starts")
        except Exception as e:
            print(f"Warning during table check: {e}")
        
        await conn.close()
        
        print("\n" + "=" * 60)
        print("Database initialization completed!")
        print("=" * 60)
        print("\nNext step: Start the backend server")
        print("Command: python start_server.py")
        
        return True
        
    except asyncpg.exceptions.PostgresError as e:
        print(f"\nPostgreSQL Error: {e}")
        print("\nPossible reasons:")
        print("1. PostgreSQL service is not running")
        print("2. Wrong password (current: 123456)")
        print("3. Wrong username (current: postgres)")
        print("4. PostgreSQL port is not 5432")
        return False
    except Exception as e:
        print(f"\nError: {e}")
        return False


async def main():
    success = await check_and_create_database()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
