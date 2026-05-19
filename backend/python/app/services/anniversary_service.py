import logging
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_, and_, func
from sqlalchemy.orm import selectinload
import uuid

from app.database import db_manager
from app.models import (
    Anniversary, AnniversaryType, RepeatType,
    PushRule, PushChannel,
    Message, MessageType, MessageStatus,
    ScheduledTask, TaskStatus,
    FamilyUser, User, Family, FamilyMember
)

logger = logging.getLogger(__name__)


def generate_id() -> str:
    return str(uuid.uuid4())


def get_anniversary_type_label(anniversary_type: str) -> str:
    labels = {
        "birthday": "生日",
        "deathday": "忌日",
        "weddingday": "结婚日",
        "sacrificialday": "祭祀日"
    }
    return labels.get(anniversary_type, anniversary_type)


async def create_reminder_message(
    db: AsyncSession,
    user_id: str,
    family_id: str,
    anniversary: Anniversary,
    advance_days: int,
    member_name: Optional[str] = None
) -> Message:
    anniversary_label = get_anniversary_type_label(anniversary.type)
    
    if advance_days == 0:
        title = f"{anniversary_label}提醒"
        if member_name:
            content = f"今天是 {member_name} 的{anniversary_label}，请记得缅怀和纪念。"
        else:
            content = f"今天是 {anniversary.name} 的{anniversary_label}，请记得缅怀和纪念。"
    elif advance_days == 1:
        title = f"{anniversary_label}提前提醒"
        if member_name:
            content = f"明天是 {member_name} 的{anniversary_label}，请提前做好准备。"
        else:
            content = f"明天是 {anniversary.name} 的{anniversary_label}，请提前做好准备。"
    else:
        title = f"{anniversary_label}提前提醒"
        if member_name:
            content = f"{advance_days}天后是 {member_name} 的{anniversary_label}（{anniversary.date}），请提前做好准备。"
        else:
            content = f"{advance_days}天后是 {anniversary.name} 的{anniversary_label}（{anniversary.date}），请提前做好准备。"

    message = Message(
        id=generate_id(),
        user_id=user_id,
        family_id=family_id,
        anniversary_id=anniversary.id,
        type=MessageType.ANNIVERSARY_REMINDER.value,
        title=title,
        content=content,
        status=MessageStatus.UNREAD.value
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    return message


async def check_anniversaries_for_reminder():
    """
    检查需要提醒的纪念日
    """
    async with db_manager.session_maker() as db:
        try:
            now = datetime.now(timezone.utc)
            today_month = now.month
            today_day = now.day
            
            logger.info(f"开始检查纪念日提醒，当前时间: {now}")

            active_anniversaries_query = (
                select(Anniversary)
                .where(
                    Anniversary.is_active == True,
                    Anniversary.deleted_at.is_(None)
                )
                .options(selectinload(Anniversary.member), selectinload(Anniversary.family))
            )
            active_anniversaries_result = await db.execute(active_anniversaries_query)
            active_anniversaries = active_anniversaries_result.scalars().all()
            
            logger.info(f"找到 {len(active_anniversaries)} 个活跃的纪念日")

            for anniversary in active_anniversaries:
                family = anniversary.family
                if not family:
                    continue

                family_users_query = (
                    select(FamilyUser)
                    .where(FamilyUser.family_id == family.id)
                    .options(selectinload(FamilyUser.user))
                )
                family_users_result = await db.execute(family_users_query)
                family_users = family_users_result.scalars().all()

                if not family_users:
                    continue

                member_name = anniversary.member.name if anniversary.member else None

                for family_user in family_users:
                    user = family_user.user
                    if not user:
                        continue

                    push_rules_query = (
                        select(PushRule)
                        .where(
                            PushRule.family_id == family.id,
                            PushRule.user_id == user.id,
                            PushRule.is_enabled == True
                        )
                    )
                    push_rules_result = await db.execute(push_rules_query)
                    push_rules = push_rules_result.scalars().all()

                    applicable_rules = []
                    for rule in push_rules:
                        if rule.anniversary_type is None:
                            applicable_rules.append(rule)
                        elif rule.anniversary_type == anniversary.type:
                            applicable_rules.append(rule)

                    if not applicable_rules:
                        default_rule = PushRule(
                            push_channels=[PushChannel.IN_APP.value],
                            advance_days=0,
                            push_time="09:00"
                        )
                        applicable_rules.append(default_rule)

                    for rule in applicable_rules:
                        advance_days = rule.advance_days
                        
                        check_date = now + timedelta(days=advance_days)
                        check_month = check_date.month
                        check_day = check_date.day

                        if anniversary.month == check_month and anniversary.day == check_day:
                            existing_message_query = (
                                select(Message)
                                .where(
                                    Message.user_id == user.id,
                                    Message.anniversary_id == anniversary.id,
                                    func.date(Message.created_at) == check_date.date()
                                )
                            )
                            existing_message_result = await db.execute(existing_message_query)
                            existing_message = existing_message_result.scalar_one_or_none()

                            if not existing_message:
                                try:
                                    await create_reminder_message(
                                        db=db,
                                        user_id=user.id,
                                        family_id=family.id,
                                        anniversary=anniversary,
                                        advance_days=advance_days,
                                        member_name=member_name
                                    )
                                    logger.info(f"为用户 {user.id} 创建了 {anniversary.name} 的{get_anniversary_type_label(anniversary.type)}提醒消息")
                                except Exception as e:
                                    logger.error(f"创建提醒消息失败: {e}")
                                    continue

            logger.info("纪念日提醒检查完成")
            
        except Exception as e:
            logger.error(f"检查纪念日提醒时发生错误: {e}", exc_info=True)


async def run_scheduled_task(task: ScheduledTask) -> ScheduledTask:
    """
    执行定时任务
    """
    async with db_manager.session_maker() as db:
        try:
            task.status = TaskStatus.RUNNING.value
            await db.commit()

            if task.task_type == "anniversary_reminder":
                await check_anniversaries_for_reminder()
                task.result = "纪念日提醒检查完成"
            elif task.task_type == "cleanup_old_tasks":
                cutoff_time = datetime.now(timezone.utc) - timedelta(days=7)
                delete_query = delete(ScheduledTask).where(
                    ScheduledTask.executed_at < cutoff_time,
                    ScheduledTask.status.in_([TaskStatus.COMPLETED.value, TaskStatus.FAILED.value])
                )
                await db.execute(delete_query)
                await db.commit()
                task.result = "清理旧任务完成"
            else:
                task.result = f"未知任务类型: {task.task_type}"

            task.status = TaskStatus.COMPLETED.value
            task.executed_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(task)

            return task

        except Exception as e:
            logger.error(f"执行定时任务失败: {e}", exc_info=True)
            task.status = TaskStatus.FAILED.value
            task.error_message = str(e)
            task.executed_at = datetime.now(timezone.utc)
            task.retry_count += 1
            await db.commit()
            await db.refresh(task)
            return task


async def check_pending_tasks():
    """
    检查并执行待处理的定时任务
    """
    async with db_manager.session_maker() as db:
        try:
            now = datetime.now(timezone.utc)

            pending_query = (
                select(ScheduledTask)
                .where(
                    ScheduledTask.status == TaskStatus.PENDING.value,
                    ScheduledTask.scheduled_time <= now
                )
                .order_by(ScheduledTask.scheduled_time)
            )
            pending_result = await db.execute(pending_query)
            pending_tasks = pending_result.scalars().all()

            for task in pending_tasks:
                await run_scheduled_task(task)

        except Exception as e:
            logger.error(f"检查待处理任务时发生错误: {e}", exc_info=True)


async def create_anniversary_reminder_task(
    db: AsyncSession,
    scheduled_time: datetime,
    anniversary_id: Optional[str] = None
) -> ScheduledTask:
    """
    创建纪念日提醒任务
    """
    task = ScheduledTask(
        id=generate_id(),
        task_name="纪念日提醒检查",
        task_type="anniversary_reminder",
        anniversary_id=anniversary_id,
        scheduled_time=scheduled_time,
        status=TaskStatus.PENDING.value,
        retry_count=0,
        max_retries=3
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    logger.info(f"创建纪念日提醒任务，计划执行时间: {scheduled_time}")
    return task


async def create_recurring_reminder_tasks():
    """
    创建定期的纪念日提醒任务
    """
    async with db_manager.session_maker() as db:
        now = datetime.now(timezone.utc)
        
        today_9am = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now > today_9am:
            today_9am += timedelta(days=1)

        existing_query = (
            select(ScheduledTask)
            .where(
                ScheduledTask.task_type == "anniversary_reminder",
                ScheduledTask.status == TaskStatus.PENDING.value,
                ScheduledTask.scheduled_time >= now
            )
        )
        existing_result = await db.execute(existing_query)
        existing_tasks = existing_result.scalars().all()

        if not existing_tasks:
            await create_anniversary_reminder_task(db, today_9am)
            
            tomorrow_9am = today_9am + timedelta(days=1)
            await create_anniversary_reminder_task(db, tomorrow_9am)

            cleanup_time = today_9am + timedelta(hours=1)
            cleanup_task = ScheduledTask(
                id=generate_id(),
                task_name="清理旧任务",
                task_type="cleanup_old_tasks",
                scheduled_time=cleanup_time,
                status=TaskStatus.PENDING.value,
                retry_count=0,
                max_retries=1
            )
            db.add(cleanup_task)
            await db.commit()


async def anniversary_reminder_worker():
    """
    纪念日提醒后台工作进程
    """
    logger.info("纪念日提醒工作进程已启动")
    
    while True:
        try:
            await check_pending_tasks()
            
            await asyncio.sleep(60)
            
        except asyncio.CancelledError:
            logger.info("纪念日提醒工作进程已取消")
            break
        except Exception as e:
            logger.error(f"纪念日提醒工作进程发生错误: {e}", exc_info=True)
            await asyncio.sleep(60)
