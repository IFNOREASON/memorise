import asyncio
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
        print("Testing get_my_family_status API logic directly")
        print("=" * 60)
        
        print(f"\n[1] Get user by id: {user_id}")
        user_stmt = select(User).where(User.id == user_id)
        user_result = await session.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            print("  User NOT found!")
            return
        
        print(f"  User found: username={user.username}")
        
        print("\n[2] Query family_users for this user (same as API logic)...")
        
        # This is the same query as in get_my_family_status API
        family_users_stmt = (
            select(FamilyUser)
            .where(FamilyUser.user_id == user_id)
            # Note: selectinload(FamilyUser.family) won't work here because FamilyUser doesn't have 'family' relationship defined
            .order_by(FamilyUser.created_at)
        )
        family_users_result = await session.execute(family_users_stmt)
        family_users = family_users_result.scalars().all()
        
        print(f"  Found {len(family_users)} family_users records")
        
        if not family_users:
            print("\n  API would return: hasFamily=False")
            return
        
        print("\n[3] Processing family_users (same as API logic)...")
        
        family_list = []
        owned_family = None
        
        for i, family_user in enumerate(family_users):
            print(f"\n  [{i+1}] family_user_id={family_user.id}")
            print(f"      family_id={family_user.family_id}")
            print(f"      role={family_user.role}")
            
            # Get family details
            family_stmt = select(Family).where(Family.id == family_user.family_id)
            family_result = await session.execute(family_stmt)
            family = family_result.scalar_one_or_none()
            
            if not family:
                print(f"      Family NOT found! Skipping...")
                continue
            
            print(f"      Family: surname={family.surname}, hall_name={family.hall_name}")
            
            # Get member count
            members_stmt = (
                select(FamilyMember)
                .where(
                    FamilyMember.family_id == family.id,
                    FamilyMember.deleted_at.is_(None)
                )
            )
            members_result = await session.execute(members_stmt)
            members_count = len(members_result.scalars().all())
            
            print(f"      Member count: {members_count}")
            
            is_head = family_user.role == FamilyRole.HEAD.value
            print(f"      Is head: {is_head}")
            
            # Build family item (same as API)
            family_item = {
                "family": {
                    "id": family.id,
                    "surname": family.surname,
                    "hall_name": family.hall_name,
                    "ancestor": family.ancestor,
                    "description": family.description,
                    "zi_bei": family.zi_bei,
                    "created_at": family.created_at,
                    "updated_at": family.updated_at
                },
                "role": family_user.role,
                "familyUser": {
                    "id": family_user.id,
                    "familyId": family_user.family_id,
                    "userId": family_user.user_id,
                    "role": family_user.role,
                    "createdAt": family_user.created_at,
                    "updatedAt": family_user.updated_at
                },
                "memberCount": members_count,
                "isHead": is_head
            }
            family_list.append(family_item)
            
            if is_head:
                owned_family = family_item
                print(f"      -> This is the owned family!")
        
        print("\n[4] API Response (simulated):")
        print(f"  hasFamily: {len(family_list) > 0}")
        print(f"  totalFamilies: {len(family_list)}")
        print(f"  ownedFamily exists: {owned_family is not None}")
        
        if owned_family:
            print(f"\n  Owned family details:")
            print(f"    surname: {owned_family['family']['surname']}")
            print(f"    hall_name: {owned_family['family']['hall_name']}")
            print(f"    role: {owned_family['role']}")
            print(f"    memberCount: {owned_family['memberCount']}")
        
        print("")
        print("=" * 60)
        print("Test completed")
        print("=" * 60)
        print("")
        
        if len(family_list) > 0:
            print("Conclusion:")
            print("  - API would return hasFamily=True")
            print("  - Frontend should show the family, not the create page")
            print("  - The problem is likely in the frontend (token not saved, or API call failing)")
        else:
            print("Conclusion:")
            print("  - API would return hasFamily=False")
            print("  - Frontend would show the create page")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_api_logic())
