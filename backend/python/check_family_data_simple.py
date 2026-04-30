import asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models import User, Family, FamilyUser, FamilyMember


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
        print(f"Check user: {user_id}")
        print("=" * 60)
        
        print("\n[1] Check user in users table...")
        user_stmt = select(User).where(User.id == user_id)
        user_result = await session.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if user:
            print(f"  User found: id={user.id}, username={user.username}, nickname={user.nickname}")
        else:
            print(f"  User NOT found!")
        
        print("\n[2] Check family_users table...")
        fu_stmt = (
            select(FamilyUser)
            .where(FamilyUser.user_id == user_id)
            .options(selectinload(FamilyUser.family))
            .order_by(FamilyUser.created_at)
        )
        fu_result = await session.execute(fu_stmt)
        family_users = fu_result.scalars().all()
        
        print(f"  Found {len(family_users)} family_users records:")
        for i, fu in enumerate(family_users):
            print(f"\n  [{i+1}] family_user_id={fu.id}")
            print(f"      family_id={fu.family_id}")
            print(f"      role={fu.role}")
            
            if fu.family:
                print(f"      Family info:")
                print(f"        id={fu.family.id}")
                print(f"        surname={fu.family.surname}")
                print(f"        hall_name={fu.family.hall_name}")
                print(f"        ancestor={fu.family.ancestor}")
                try:
                    print(f"        head_user_id={fu.family.head_user_id}")
                except AttributeError:
                    print(f"        head_user_id=N/A (column may not exist)")
            else:
                print(f"      Associated family NOT found!")
        
        print("\n[3] Check families table by head_user_id...")
        try:
            family_stmt = select(Family).where(Family.head_user_id == user_id)
            family_result = await session.execute(family_stmt)
            owned_families = family_result.scalars().all()
            
            print(f"  Found {len(owned_families)} families by head_user_id={user_id}:")
            for i, f in enumerate(owned_families):
                print(f"\n  [{i+1}] family_id={f.id}")
                print(f"      surname={f.surname}")
                print(f"      hall_name={f.hall_name}")
                print(f"      head_user_id={f.head_user_id}")
        except Exception as e:
            print(f"  Query failed (head_user_id column may not exist): {e}")
        
        print("\n[4] Check all families...")
        all_families_stmt = select(Family).order_by(Family.created_at)
        all_families_result = await session.execute(all_families_stmt)
        all_families = all_families_result.scalars().all()
        
        print(f"  Total families in database: {len(all_families)}")
        for i, f in enumerate(all_families):
            print(f"\n  [{i+1}] family_id={f.id}")
            print(f"      surname={f.surname}")
            print(f"      hall_name={f.hall_name}")
            try:
                print(f"      head_user_id={f.head_user_id}")
            except AttributeError:
                print(f"      head_user_id=N/A (column may not exist)")
        
        print("\n[5] Check if head_user_id column exists...")
        try:
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
                print(f"  head_user_id column EXISTS in families table")
            else:
                print(f"  head_user_id column DOES NOT EXIST in families table")
                print(f"  You need to run: py migrate_add_head_user_id.py")
        except Exception as e:
            print(f"  Error checking column: {e}")
        
        print("")
        print("=" * 60)
        print("Check completed")
        print("=" * 60)
        print("")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_data())
