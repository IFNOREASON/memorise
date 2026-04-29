import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"


async def test_health_check():
    """测试健康检查接口"""
    print("\n" + "=" * 50)
    print("测试 1: 健康检查接口")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/")
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"错误: {e}")
            return False


async def test_register():
    """测试注册接口"""
    print("\n" + "=" * 50)
    print("测试 2: 注册接口")
    print("=" * 50)
    
    test_user = {
        "username": "test_user_001",
        "password": "123456",
        "confirm_password": "123456",
        "nickname": "测试用户"
    }
    
    print(f"请求数据: {json.dumps(test_user, ensure_ascii=False)}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            )
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            try:
                print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
            except:
                print(f"响应文本: {response.text}")
            return response.status_code in [200, 201, 400]
        except Exception as e:
            print(f"错误: {e}")
            return False


async def test_register_invalid():
    """测试注册接口 - 密码不一致"""
    print("\n" + "=" * 50)
    print("测试 3: 注册接口 - 密码不一致")
    print("=" * 50)
    
    test_user = {
        "username": "test_user_002",
        "password": "123456",
        "confirm_password": "654321",
        "nickname": "测试用户2"
    }
    
    print(f"请求数据: {json.dumps(test_user, ensure_ascii=False)}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            )
            print(f"状态码: {response.status_code}")
            try:
                print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
            except:
                print(f"响应文本: {response.text}")
            return response.status_code == 422 or response.status_code == 400
        except Exception as e:
            print(f"错误: {e}")
            return False


async def test_login():
    """测试登录接口"""
    print("\n" + "=" * 50)
    print("测试 4: 登录接口")
    print("=" * 50)
    
    # 先注册一个用户
    test_user = {
        "username": "test_user_login",
        "password": "123456",
        "confirm_password": "123456",
        "nickname": "登录测试用户"
    }
    
    async with httpx.AsyncClient() as client:
        # 先注册
        try:
            await client.post(f"{BASE_URL}/api/register", json=test_user)
        except:
            pass
        
        # 然后登录
        login_data = {
            "username": "test_user_login",
            "password": "123456"
        }
        
        print(f"登录请求数据: {json.dumps(login_data, ensure_ascii=False)}")
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"状态码: {response.status_code}")
            try:
                print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
            except:
                print(f"响应文本: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"错误: {e}")
            return False


async def test_login_wrong_password():
    """测试登录接口 - 错误密码"""
    print("\n" + "=" * 50)
    print("测试 5: 登录接口 - 错误密码")
    print("=" * 50)
    
    login_data = {
        "username": "test_user_login",
        "password": "wrong_password"
    }
    
    print(f"登录请求数据: {json.dumps(login_data, ensure_ascii=False)}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"状态码: {response.status_code}")
            try:
                print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
            except:
                print(f"响应文本: {response.text}")
            return response.status_code == 401
        except Exception as e:
            print(f"错误: {e}")
            return False


async def test_cors_preflight():
    """测试 CORS 预检请求"""
    print("\n" + "=" * 50)
    print("测试 6: CORS 预检请求")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.options(
                f"{BASE_URL}/api/register",
                headers={
                    "Origin": "http://localhost:5173",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                }
            )
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            # 检查 CORS 相关头
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
            }
            print(f"CORS 头: {json.dumps(cors_headers, ensure_ascii=False, indent=2)}")
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"错误: {e}")
            return False


async def main():
    print("=" * 60)
    print("认证功能测试")
    print("=" * 60)
    print(f"后端地址: {BASE_URL}")
    
    results = {}
    
    # 健康检查
    results["健康检查"] = await test_health_check()
    
    # 注册测试
    results["注册接口"] = await test_register()
    
    # 注册验证测试
    results["注册-密码不一致"] = await test_register_invalid()
    
    # 登录测试
    results["登录接口"] = await test_login()
    
    # 登录错误测试
    results["登录-错误密码"] = await test_login_wrong_password()
    
    # CORS 测试
    results["CORS 预检"] = await test_cors_preflight()
    
    # 输出总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("所有测试通过！")
    else:
        print("部分测试失败，请检查后端服务和配置。")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
