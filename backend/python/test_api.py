import httpx
import asyncio

BASE_URL = "http://localhost:8001"

async def check_data():
    async with httpx.AsyncClient() as client:
        print("=== 检查数字人列表 ===")
        response = await client.get(f"{BASE_URL}/api/avatars")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        
        if data.get("success") and data.get("data"):
            avatars = data["data"].get("avatars", [])
            print(f"\n数字人数量: {len(avatars)}")
            for avatar in avatars:
                print(f"  - ID: {avatar.get('id')}, 名称: {avatar.get('name')}, 语音模型ID: {avatar.get('voice_model_id')}")
        
        print("\n=== 检查声音素材列表 ===")
        response = await client.get(f"{BASE_URL}/api/voice/materials")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        
        if data.get("success") and data.get("data"):
            materials = data["data"].get("materials", [])
            print(f"\n声音素材数量: {len(materials)}")
            for m in materials:
                print(f"  - ID: {m.get('id')}, AvatarID: {m.get('avatar_id')}, 名称: {m.get('name')}, 状态: {m.get('status')}, 时长: {m.get('duration')}秒, URL: {m.get('audio_url')}")
        
        print("\n=== 检查声音模型列表 ===")
        response = await client.get(f"{BASE_URL}/api/voice/models")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        
        if data.get("success") and data.get("data"):
            models = data["data"].get("models", [])
            print(f"\n声音模型数量: {len(models)}")
            for m in models:
                print(f"  - ID: {m.get('id')}, AvatarID: {m.get('avatar_id')}, 名称: {m.get('name')}, 状态: {m.get('status')}, 进度: {m.get('progress')}%, 模型URL: {m.get('model_url')}")

if __name__ == "__main__":
    asyncio.run(check_data())
