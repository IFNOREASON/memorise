"""
Test avatar creation API
"""

import base64
import sys
import requests
import json

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


def test_health():
    print("Testing health check...")
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=10)
        print(f"  Status: {r.status_code}")
        print(f"  Response: {json.dumps(r.json(), ensure_ascii=False, indent=2)}")
        return r.status_code == 200
    except Exception as e:
        print(f"  Error: {e}")
        return False


def test_get_avatars():
    print("\nTesting get avatars...")
    try:
        r = requests.get(f"{API_BASE_URL}/avatars", timeout=10)
        print(f"  Status: {r.status_code}")
        data = r.json()
        if data.get("success") and data.get("data"):
            avatars = data["data"].get("avatars", [])
            print(f"  Total: {data['data'].get('total', 0)}")
            for a in avatars:
                print(f"    - {a.get('name')} ({a.get('id')}) - status: {a.get('status')}")
        else:
            print(f"  Response: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"  Error: {e}")


def test_create_avatar():
    print("\nTesting avatar creation...")
    
    photos_base64 = []
    for path in PHOTO_PATHS:
        import os
        if os.path.exists(path):
            b64 = image_to_base64(path)
            photos_base64.append(b64)
            print(f"  Loaded: {path} ({len(b64)} chars)")
        else:
            print(f"  Warning: File not found: {path}")
    
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
    
    print(f"  Sending request with {len(photos_base64)} photos...")
    print(f"  Name: {create_request['name']}")
    print(f"  Method: {create_request['generationMethod']}")
    
    try:
        r = requests.post(
            f"{API_BASE_URL}/avatars/generate",
            json=create_request,
            timeout=120
        )
        print(f"\n  Status code: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"\n  Success!")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get("success") and data.get("data"):
                avatar_id = data["data"].get("avatarId")
                if avatar_id:
                    print(f"\n  Polling status for avatar: {avatar_id}")
                    import time
                    for i in range(10):
                        time.sleep(3)
                        try:
                            r2 = requests.get(f"{API_BASE_URL}/avatars/{avatar_id}/status", timeout=10)
                            if r2.status_code == 200:
                                status_data = r2.json()
                                if status_data.get("success") and status_data.get("data"):
                                    s = status_data["data"].get("status")
                                    p = status_data["data"].get("progress", 0)
                                    print(f"    [{i+1}/10] status: {s}, progress: {p}%")
                                    
                                    if s in ["active", "completed", "failed", "retry_pending"]:
                                        print(f"\n  Final status: {s}")
                                        if status_data["data"].get("lastError"):
                                            print(f"  Error: {status_data['data']['lastError']}")
                                        break
                            else:
                                print(f"    [{i+1}/10] status code: {r2.status_code}")
                        except Exception as e:
                            print(f"    [{i+1}/10] error: {e}")
            
            return data
        else:
            print(f"  Failed!")
            print(f"  Response: {r.text[:500]}")
            return None
            
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("=" * 60)
    print("Test Avatar Creation API")
    print("=" * 60)
    
    print(f"\nAPI URL: {API_BASE_URL}")
    print(f"Test photos: {len(PHOTO_PATHS)}")
    
    if test_health():
        test_get_avatars()
        test_create_avatar()
        test_get_avatars()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
