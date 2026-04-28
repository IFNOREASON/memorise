"""
测试照片创建数字人接口的脚本
"""

import base64
import asyncio
import httpx
import json
import sys
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE_URL = "http://localhost:8000/api"

PHOTO_PATHS = [
    r"D:\tools\豆包 (1).png",
    r"D:\tools\豆包 (2).png",
    r"D:\tools\豆包 (3).png",
    r"D:\tools\豆包 (4).png",
    r"D:\tools\豆包 (5).png",
]


def image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def test_health():
    print("Testing health check...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{API_BASE_URL}/health")
            data = response.json()
            print(f"  OK: {json.dumps(data, ensure_ascii=False)}")
            return True
        except Exception as e:
            print(f"  FAIL: {e}")
            return False


async def test_analyze_photos():
    print("\nTesting photo analysis...")
    
    photos_base64 = []
    for path in PHOTO_PATHS:
        if Path(path).exists():
            base64_str = image_to_base64(path)
            photos_base64.append(base64_str)
            print(f"  Loaded: {path} (size: {len(base64_str)} chars)")
        else:
            print(f"  Warning: File not found {path}")
    
    if len(photos_base64) < 1:
        print("  No photos available")
        return None
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/photos/analyze",
                json={"photos": photos_base64}
            )
            data = response.json()
            print(f"  Result:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        except Exception as e:
            print(f"  FAIL: {e}")
            import traceback
            traceback.print_exc()
            return None


async def test_create_avatar_from_photos():
    print("\nTesting avatar creation from photos...")
    
    photos_base64 = []
    for path in PHOTO_PATHS:
        if Path(path).exists():
            base64_str = image_to_base64(path)
            photos_base64.append(base64_str)
    
    if len(photos_base64) < 1:
        print("  No photos available")
        return None
    
    create_request = {
        "name": "TestDoubao",
        "relationship": "Friend",
        "gender": "male",
        "birthYear": "2020",
        "description": "Test avatar created from photos",
        "generationMethod": "photo",
        "photos": photos_base64
    }
    
    print(f"  Request:")
    print(f"    - name: {create_request['name']}")
    print(f"    - relationship: {create_request['relationship']}")
    print(f"    - gender: {create_request['gender']}")
    print(f"    - photo count: {len(photos_base64)}")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            print("\n  Sending request...")
            response = await client.post(
                f"{API_BASE_URL}/avatars/generate",
                json=create_request
            )
            
            print(f"  Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n  Success!")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                if data.get("success") and data.get("data"):
                    avatar_id = data["data"].get("avatarId")
                    task_id = data["data"].get("taskId")
                    
                    print(f"\n  Polling status...")
                    await poll_avatar_status(client, avatar_id)
                
                return data
            else:
                print(f"  FAIL: {response.status_code}")
                print(f"  Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"  FAIL: {e}")
            import traceback
            traceback.print_exc()
            return None


async def poll_avatar_status(client: httpx.AsyncClient, avatar_id: str, max_polls: int = 10):
    for i in range(max_polls):
        try:
            response = await client.get(f"{API_BASE_URL}/avatars/{avatar_id}/status")
            data = response.json()
            
            if data.get("success") and data.get("data"):
                status_data = data["data"]
                status = status_data.get("status")
                progress = status_data.get("progress", 0)
                
                print(f"    [{i+1}/{max_polls}] status: {status}, progress: {progress}%")
                
                if status in ["active", "completed", "failed", "retry_pending"]:
                    print(f"\n  Final status: {status}")
                    if status_data.get("lastError"):
                        print(f"  Error: {status_data['lastError']}")
                    break
            else:
                print(f"    [{i+1}/{max_polls}] unable to get status")
            
            await asyncio.sleep(3)
            
        except Exception as e:
            print(f"    [{i+1}/{max_polls}] error: {e}")
            await asyncio.sleep(3)


async def test_get_avatars():
    print("\nTesting get avatars...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{API_BASE_URL}/avatars")
            data = response.json()
            if data.get("success") and data.get("data"):
                avatars = data["data"].get("avatars", [])
                print(f"  Total: {data['data'].get('total', 0)}")
                for avatar in avatars:
                    print(f"    - {avatar.get('name')} ({avatar.get('id')}) - status: {avatar.get('status')}")
            else:
                print(f"  Warning: {data}")
        except Exception as e:
            print(f"  FAIL: {e}")


async def main():
    print("=" * 60)
    print("Test Avatar Creation API")
    print("=" * 60)
    
    print(f"\nAPI URL: {API_BASE_URL}")
    print(f"Test photos: {len(PHOTO_PATHS)}")
    
    health_ok = await test_health()
    
    if health_ok:
        await test_get_avatars()
        await test_analyze_photos()
        await test_create_avatar_from_photos()
        await test_get_avatars()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
