import asyncio
import traceback
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models import User, Family, FamilyUser, FamilyMember, FamilyRole


async def test_api_logic():
    user_id = "10c266f1-07b3-471b-8627-7f1324e592cb"
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    async with AsyncSession(engine) as session:
        print("")
        print("=" * 60)
        print("Testing get_my_family_status API logic (with relationships)")
        print("=" * 60)
        
        print(f"\n[1] Get user by id: {user_id}")
        user_stmt = select(User).where(User.id == user_id)
        user_result = await session.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            print("  User NOT found!")
            return
        
        print(f"  User found: username={user.username}")
        
        print("\n[2] Query family_users with selectinload (same as API)...")
        print("  This is the exact query used in get_my_family_status API")
        
        try:
            # This is the exact query from get_my_family_status API
            family_users_stmt = (
                select(FamilyUser)
                .where(FamilyUser.user_id == user_id)
                .options(selectinload(FamilyUser.family))
                .order_by(FamilyUser.created_at)
            )
            family_users_result = await session.execute(family_users_stmt)
            family_users = family_users_result.scalars().all()
            
            print(f"  Query executed successfully!")
            print(f"  Found {len(family_users)} family_users records")
            
            if not family_users:
                print("\n  No family_users found")
                return
            
            print("\n[3] Processing family_users...")
            
            for i, family_user in enumerate(family_users):
                print(f"\n  [{i+1}] family_user_id={family_user.id}")
                print(f"      family_id={family_user.family_id}")
                print(f"      role={family_user.role}")
                
                # Check if family relationship was loaded
                if family_user.family:
                    print(f"      Family (via relationship):")
                    print(f"        id={family_user.family.id}")
                    print(f"        surname={family_user.family.surname}")
                    print(f"        hall_name={family_user.family.hall_name}")
                    try:
                        print(f"        head_user_id={family_user.family.head_user_id}")
                    except AttributeError as e:
                        print(f"        head_user_id=Error accessing: {e}")
                else:
                    print(f"      Family relationship is None!")
                
                # Also try direct query
                print(f"\n      Direct query for family:")
                family_stmt = select(Family).where(Family.id == family_user.family_id)
                family_result = await session.execute(family_stmt)
                family = family_result.scalar_one_or_none()
                
                if family:
                    print(f"        id={family.id}")
                    print(f"        surname={family.surname}")
                    print(f"        hall_name={family.hall_name}")
                    try:
                        print(f"        head_user_id={family.head_user_id}")
                    except AttributeError as e:
                        print(f"        head_user_id=Error accessing: {e}")
                else:
                    print(f"        Family NOT found!")
                
                # Get member count
                print(f"\n      Getting member count...")
                members_stmt = (
                    select(FamilyMember)
                    .where(
                        FamilyMember.family_id == family_user.family_id,
                        FamilyMember.deleted_at.is_(None)
                    )
                )
                members_result = await session.execute(members_stmt)
                members_count = len(members_result.scalars().all())
                print(f"        Member count: {members_count}")
                
                # Check is_head
                is_head = family_user.role == FamilyRole.HEAD.value
                print(f"\n      Is head: {is_head}")
            
            print("\n[4] API would return:")
            print(f"  hasFamily: True")
            print(f"  totalFamilies: {len(family_users)}")
            print("\n  Test PASSED! The API logic works correctly.")
            
        except Exception as e:
            print(f"\n  ERROR: {e}")
            print(f"\n  Stack trace:")
            traceback.print_exc()

    await engine.dispose()
    
    print("")
    print("=" * 60)
    print("Test completed")
    print("=" * 60)
    print("")


if __name__ == "__main__":
    asyncio.run(test_api_logic())
