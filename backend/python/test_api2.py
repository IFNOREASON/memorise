import httpx
import asyncio
import json

BASE_URL = "http://localhost:8001"

async def check_data():
    results = {}
    
    async with httpx.AsyncClient() as client:
        print("=== 检查数字人列表 ===")
        response = await client.get(f"{BASE_URL}/api/avatars")
        results["avatars"] = response.json()
        print(f"Status: {response.status_code}")
        print(json.dumps(results["avatars"], ensure_ascii=False, indent=2))
        
        print("\n=== 检查声音素材列表 ===")
        response = await client.get(f"{BASE_URL}/api/voice/materials")
        results["materials"] = response.json()
        print(f"Status: {response.status_code}")
        print(json.dumps(results["materials"], ensure_ascii=False, indent=2))
        
        print("\n=== 检查声音模型列表 ===")
        response = await client.get(f"{BASE_URL}/api/voice/models")
        results["models"] = response.json()
        print(f"Status: {response.status_code}")
        print(json.dumps(results["models"], ensure_ascii=False, indent=2))
    
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n结果已保存到 test_results.json")

if __name__ == "__main__":
    asyncio.run(check_data())
