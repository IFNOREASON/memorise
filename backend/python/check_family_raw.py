import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.config import settings


async def check_data():
    user_id = "10c266f1-07b3-471b-8627-7f1324e592cb"
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    async with AsyncSession(engine) as session:
        print("")
        print("=" * 60)
        print(f"Check user: {user_id} (username: yang)")
        print("=" * 60)
        
        print("\n[1] Check family_users table...")
        result = await session.execute(text(
            """
            SELECT fu.id, fu.family_id, fu.user_id, fu.role, fu.created_at,
                   f.surname, f.hall_name, f.ancestor
            FROM family_users fu
            LEFT JOIN families f ON fu.family_id = f.id
            WHERE fu.user_id = :user_id
            ORDER BY fu.created_at
            """
        ), {"user_id": user_id})
        
        rows = result.fetchall()
        print(f"  Found {len(rows)} records:")
        
        for i, row in enumerate(rows):
            print(f"\n  [{i+1}] family_user_id={row[0]}")
            print(f"      family_id={row[1]}")
            print(f"      user_id={row[2]}")
            print(f"      role={row[3]}")
            print(f"      created_at={row[4]}")
            print(f"      surname={row[5]}")
            print(f"      hall_name={row[6]}")
            print(f"      ancestor={row[7]}")
        
        print("\n[2] Check if head_user_id column exists in families...")
        result = await session.execute(text(
            """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'families' 
            AND column_name = 'head_user_id'
            """
        ))
        column_exists = result.scalar_one_or_none()
        
        if column_exists:
            print("  head_user_id column EXISTS")
            
            print("\n[3] Check families by head_user_id...")
            result = await session.execute(text(
                """
                SELECT id, surname, hall_name, ancestor, head_user_id, created_at
                FROM families
                WHERE head_user_id = :user_id
                ORDER BY created_at
                """
            ), {"user_id": user_id})
            
            rows = result.fetchall()
            print(f"  Found {len(rows)} families where head_user_id={user_id}:")
            
            for i, row in enumerate(rows):
                print(f"\n  [{i+1}] family_id={row[0]}")
                print(f"      surname={row[1]}")
                print(f"      hall_name={row[2]}")
                print(f"      ancestor={row[3]}")
                print(f"      head_user_id={row[4]}")
                print(f"      created_at={row[5]}")
        else:
            print("  head_user_id column DOES NOT EXIST!")
            print("")
            print("  You need to run the migration script:")
            print("    py migrate_add_head_user_id.py")
            print("")
            print("  This will:")
            print("    1. Add head_user_id column to families table")
            print("    2. Add index and foreign key constraint")
            print("    3. Sync existing data from family_users.role='head' to families.head_user_id")
        
        print("\n[4] Check all families...")
        result = await session.execute(text(
            """
            SELECT id, surname, hall_name, ancestor, created_at
            FROM families
            ORDER BY created_at
            """
        ))
        
        rows = result.fetchall()
        print(f"  Total families in database: {len(rows)}")
        
        for i, row in enumerate(rows):
            print(f"\n  [{i+1}] family_id={row[0]}")
            print(f"      surname={row[1]}")
            print(f"      hall_name={row[2]}")
            print(f"      ancestor={row[3]}")
            print(f"      created_at={row[4]}")
        
        print("")
        print("=" * 60)
        print("Check completed")
        print("=" * 60)
        print("")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_data())
