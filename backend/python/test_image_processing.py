"""
AI影像处理模块测试脚本

功能列表:
1. 老照片修复 (RESTORATION)
2. 高清放大 (ENHANCEMENT)
3. 动态肖像生成 (DYNAMIC_PORTRAIT)
4. 跨年代合照合成 (CROSS_GENERATION)
5. 视频集锦生成 (VIDEO_HIGHLIGHTS)
6. AI场景生成 (AI_SCENE)

支持功能:
- 异步处理
- 任务队列
- 进度查询
- 结果回调
- 批量上传
- 高清导出
- 水印添加
- 格式转换
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from sqlalchemy import select, text
from app.database import AsyncSessionLocal
from app.models import Gallery, GalleryMedia
from app.schemas import (
    CreateProcessTaskRequest, BatchProcessRequest,
    ImageProcessType, ExportOptions
)
from app.services.image_processing_service import image_processing_service


async def test_create_gallery(db):
    """创建测试影集"""
    print("\n=== 1. 创建测试影集 ===")
    
    stmt = select(Gallery).limit(1)
    result = await db.execute(stmt)
    gallery = result.scalar_one_or_none()
    
    if not gallery:
        gallery = Gallery(
            id=f"test_gallery_001",
            family_id="default_family",
            name="测试影集",
            type="image",
            status="draft"
        )
        db.add(gallery)
        await db.commit()
        await db.refresh(gallery)
        print(f"✅ 创建测试影集: {gallery.id}")
    else:
        print(f"✅ 使用现有影集: {gallery.id}")
    
    return gallery.id


async def test_create_task(db, gallery_id):
    """测试创建单个处理任务"""
    print("\n=== 2. 创建老照片修复任务 ===")
    
    request = CreateProcessTaskRequest(
        galleryId=gallery_id,
        taskType=ImageProcessType.RESTORATION,
        sourceUrl="/uploads/test_photo.jpg",
        restorationParams={
            "removeScratches": True,
            "removeStains": True,
            "restoreColor": True,
            "sharpenDetails": True,
            "denoiseStrength": 70,
            "upscaleFactor": 2
        },
        exportOptions=ExportOptions(
            format="jpg",
            quality=95,
            addWatermark=True,
            watermarkText="Memorise",
            watermarkPosition="bottom_right"
        )
    )
    
    result = await image_processing_service.create_process_task(db, request)
    print(f"✅ 创建任务成功: {result.taskId}")
    print(f"   类型: {result.taskType}")
    print(f"   状态: {result.status}")
    print(f"   消息: {result.message}")
    
    return result.taskId


async def test_get_task_status(db, task_id):
    """测试获取任务状态"""
    print("\n=== 3. 查询任务状态 ===")
    
    result = await image_processing_service.get_task_status(db, task_id)
    print(f"✅ 任务ID: {result.taskId}")
    print(f"   状态: {result.status}")
    print(f"   进度: {result.progress}%")
    print(f"   创建时间: {result.createdAt}")


async def test_batch_tasks(db, gallery_id):
    """测试批量创建任务"""
    print("\n=== 4. 批量创建处理任务 ===")
    
    request = BatchProcessRequest(
        galleryId=gallery_id,
        mediaIds=["media1", "media2", "media3"],
        taskType=ImageProcessType.ENHANCEMENT,
        enhancementParams={
            "upscaleFactor": 4,
            "enhanceFace": True,
            "sharpen": True,
            "colorEnhance": True
        },
        exportOptions=ExportOptions(
            format="png",
            quality=100
        )
    )
    
    result = await image_processing_service.batch_create_tasks(db, request)
    print(f"✅ 批量创建成功: {result.totalTasks} 个任务")
    for task_id in result.taskIds:
        print(f"   - {task_id}")
    
    return result.taskIds


async def test_get_gallery_tasks(db, gallery_id):
    """测试获取影集任务列表"""
    print("\n=== 5. 获取影集任务列表 ===")
    
    result = await image_processing_service.get_gallery_tasks(db, gallery_id, limit=10)
    print(f"✅ 总任务数: {result.total}")
    for task in result.tasks:
        print(f"   - {task.taskId}: {task.taskType.value} - {task.status.value} ({task.progress}%)")


async def test_task_types():
    """显示支持的处理类型"""
    print("\n=== 6. 支持的AI影像处理类型 ===")
    types_info = [
        ("RESTORATION", "老照片修复", "去除划痕、污渍，恢复色彩，高清还原"),
        ("ENHANCEMENT", "高清放大", "AI超分辨率增强，放大不失真"),
        ("DYNAMIC_PORTRAIT", "动态肖像生成", "让静态照片动起来，眨眼、微笑"),
        ("CROSS_GENERATION", "跨年代合照合成", "合成不同年代的照片"),
        ("VIDEO_HIGHLIGHTS", "视频集锦生成", "多张照片合成精彩视频"),
        ("AI_SCENE", "AI场景生成", "根据描述生成AI场景")
    ]
    for type_id, name, desc in types_info:
        print(f"  ✅ {name} ({type_id})")
        print(f"     {desc}")


async def test_export_formats():
    """显示支持的导出格式"""
    print("\n=== 7. 支持的导出格式 ===")
    formats = [
        ("jpg", "JPEG图像", "通用有损压缩格式"),
        ("png", "PNG图像", "无损压缩，支持透明"),
        ("webp", "WebP图像", "Google高效格式"),
        ("mp4", "MP4视频", "通用视频格式"),
        ("gif", "GIF动图", "动态图像格式")
    ]
    for fmt, name, desc in formats:
        print(f"  ✅ {name} (.{fmt})")
        print(f"     {desc}")


async def main():
    print("=" * 60)
    print("AI影像处理模块 - 功能测试")
    print("=" * 60)
    
    await image_processing_service.start_worker()
    print("✅ 队列工作器已启动")
    
    async with AsyncSessionLocal() as db:
        try:
            gallery_id = await test_create_gallery(db)
            task_id = await test_create_task(db, gallery_id)
            
            await asyncio.sleep(0.5)
            await test_get_task_status(db, task_id)
            
            await test_batch_tasks(db, gallery_id)
            await test_get_gallery_tasks(db, gallery_id)
            await test_task_types()
            await test_export_formats()
            
            print("\n" + "=" * 60)
            print("所有测试完成！")
            print("=" * 60)
            
            print("\nAPI端点列表:")
            print("  POST /api/image-processing/tasks          - 创建任务")
            print("  POST /api/image-processing/tasks/batch    - 批量创建")
            print("  GET  /api/image-processing/tasks/{id}  - 查询状态")
            print("  GET  /api/image-processing/galleries/{id}/tasks - 任务列表")
            print("  POST /api/image-processing/tasks/{id}/retry  - 重试任务")
            print("  POST /api/image-processing/tasks/{id}/cancel - 取消任务")
            print("  GET  /api/image-processing/tasks/{id}/result   - 获取结果")
            print("  GET  /api/image-processing/types              - 处理类型")
            print("  GET  /api/image-processing/export/formats   - 导出格式")
            print("  GET  /api/image-processing/health             - 健康检查")
            
        finally:
            await image_processing_service.stop_worker()


if __name__ == "__main__":
    asyncio.run(main())
