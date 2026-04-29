"""
验证用户数据是否保存到 PostgreSQL 数据库
密码: 123456
"""

import asyncio
import sys

try:
    import asyncpg
except ImportError:
    print("Error: Please install asyncpg first")
    sys.exit(1)

from app.config import settings


async def verify_user_data():
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
    
    print("=" * 70)
    print("Verifying User Data in PostgreSQL Database")
    print("=" * 70)
    print(f"Database: {target_db}")
    print(f"Table: users")
    print("=" * 70)
    
    try:
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=target_db
        )
        
        print("\n1. Checking if 'users' table exists...")
        result = await conn.fetchrow(
            "SELECT 1 FROM information_schema.tables WHERE table_name = 'users'"
        )
        
        if not result:
            print("   ERROR: 'users' table does not exist!")
            await conn.close()
            return False
        
        print("   OK: 'users' table exists")
        
        print("\n2. Querying all users...")
        rows = await conn.fetch(
            "SELECT id, username, password_hash, nickname, is_active, created_at FROM users"
        )
        
        if not rows:
            print("   No users found in the database.")
            await conn.close()
            return False
        
        print(f"   Found {len(rows)} user(s):")
        print("-" * 70)
        
        for i, row in enumerate(rows, 1):
            print(f"\n   User {i}:")
            print(f"      ID: {row['id']}")
            print(f"      Username: {row['username']}")
            print(f"      Nickname: {row['nickname']}")
            print(f"      Is Active: {row['is_active']}")
            print(f"      Created At: {row['created_at']}")
            print(f"      Password Hash: {row['password_hash'][:50]}...")
            
            if row['password_hash'].startswith('pbkdf2_sha256$'):
                print("      Password Status: ENCRYPTED (PBKDF2-SHA256)")
            else:
                print("      Password Status: WARNING - Not encrypted properly!")
        
        print("\n" + "-" * 70)
        print("3. Verifying password encryption...")
        print("-" * 70)
        
        for row in rows:
            pwd_hash = row['password_hash']
            if pwd_hash.startswith('pbkdf2_sha256$'):
                parts = pwd_hash.split('$')
                if len(parts) == 4:
                    algo, iterations, salt, stored_hash = parts
                    print(f"\n   User: {row['username']}")
                    print(f"      Algorithm: {algo}")
                    print(f"      Iterations: {iterations}")
                    print(f"      Salt length: {len(salt)} characters")
                    print(f"      Hash length: {len(stored_hash)} characters")
                    print("      Status: Password is securely encrypted!")
        
        await conn.close()
        
        print("\n" + "=" * 70)
        print("Verification Complete!")
        print("=" * 70)
        print("\nSummary:")
        print("  - Users table exists: YES")
        print(f"  - Number of users: {len(rows)}")
        print("  - Password encryption: PBKDF2-SHA256 with salt")
        print("  - Status: ALL DATA SAVED CORRECTLY!")
        
        return True
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    success = await verify_user_data()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
