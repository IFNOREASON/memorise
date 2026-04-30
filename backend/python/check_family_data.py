import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models import User, Family, FamilyUser, FamilyMember


async def check_data():
    user_id = "10c266f1-07b3-471b-8627-7f1324e592cb"
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
        pool_pre_ping=True,
    )

    async with AsyncSession(engine) as session:
        print(f"\n{'='*60}")
        print(f"检查用户: {user_id}")
        print(f"{'='*60}")
        
        print("\n[1] 检查 users 表中的用户...")
        user_stmt = select(User).where(User.id == user_id)
        user_result = await session.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if user:
            print(f"  ✓ 找到用户: id={user.id}, username={user.username}, nickname={user.nickname}")
        else:
            print(f"  ✗ 用户不存在!")
        
        print("\n[2] 检查 family_users 表中的记录...")
        fu_stmt = (
            select(FamilyUser)
            .where(FamilyUser.user_id == user_id)
            .options(selectinload(FamilyUser.family))
            .order_by(FamilyUser.created_at)
        )
        fu_result = await session.execute(fu_stmt)
        family_users = fu_result.scalars().all()
        
        print(f"  找到 {len(family_users)} 条 family_users 记录:")
        for i, fu in enumerate(family_users):
            print(f"\n  [{i+1}] family_user_id={fu.id}")
            print(f"      family_id={fu.family_id}")
            print(f"      role={fu.role}")
            print(f"      created_at={fu.created_at}")
            
            if fu.family:
                print(f"      家族信息:")
                print(f"        id={fu.family.id}")
                print(f"        surname={fu.family.surname}")
                print(f"        hall_name={fu.family.hall_name}")
                print(f"        ancestor={fu.family.ancestor}")
                print(f"        head_user_id={fu.family.head_user_id if hasattr(fu.family, 'head_user_id') else 'N/A (字段不存在)'}")
            else:
                print(f"      ✗ 关联的家族不存在!")
        
        print("\n[3] 检查 families 表 (通过 head_user_id)...")
        try:
            family_stmt = select(Family).where(Family.head_user_id == user_id)
            family_result = await session.execute(family_stmt)
            owned_families = family_result.scalars().all()
            
            print(f"  找到 {len(owned_families)} 条 families 记录 (head_user_id={user_id}):")
            for i, f in enumerate(owned_families):
                print(f"\n  [{i+1}] family_id={f.id}")
                print(f"      surname={f.surname}")
                print(f"      hall_name={f.hall_name}")
                print(f"      ancestor={f.ancestor}")
                print(f"      head_user_id={f.head_user_id}")
                
                members_stmt = (
                    select(FamilyMember)
                    .where(
                        FamilyMember.family_id == f.id,
                        FamilyMember.deleted_at.is_(None)
                    )
                )
                members_result = await session.execute(members_stmt)
                members = members_result.scalars().all()
                print(f"      成员数量: {len(members)}")
        except Exception as e:
            print(f"  ✗ 查询失败 (可能 head_user_id 字段不存在): {e}")
        
        print("\n[4] 检查所有 families 表记录...")
        all_families_stmt = select(Family).order_by(Family.created_at)
        all_families_result = await session.execute(all_families_stmt)
        all_families = all_families_result.scalars().all()
        
        print(f"  数据库中共有 {len(all_families)} 个家族:")
        for i, f in enumerate(all_families):
            print(f"\n  [{i+1}] family_id={f.id}")
            print(f"      surname={f.surname}")
            print(f"      hall_name={f.hall_name}")
            print(f"      ancestor={f.ancestor}")
            try:
                print(f"      head_user_id={f.head_user_id}")
            except AttributeError:
                print(f"      head_user_id=N/A (字段不存在)")
            print(f"      created_at={f.created_at}")
        
        print(f"\n{'='*60}")
        print("检查完成")
        print(f"{'='*60}\n")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_data())
