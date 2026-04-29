"""诊断脚本：检查后端路由配置和代码语法"""
import sys
import os

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("诊断报告")
print("=" * 60)

print("\n1. 检查 auth.py 是否存在...")
auth_path = os.path.join(backend_dir, 'routers', 'auth.py')
if os.path.exists(auth_path):
    print(f"   ✅ auth.py 存在: {auth_path}")
else:
    print(f"   ❌ auth.py 不存在")
    sys.exit(1)

print("\n2. 检查 auth.py 中的关键代码...")
with open(auth_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'verify-password' in content:
    print("   ✅ 找到 '/verify-password' 端点定义")
else:
    print("   ❌ 未找到 '/verify-password' 端点定义")

if 'verify_user_password' in content:
    print("   ✅ 找到 'verify_user_password' 函数定义")
else:
    print("   ❌ 未找到 'verify_user_password' 函数定义")

if 'VerifyPasswordRequest' in content:
    print("   ✅ 找到 'VerifyPasswordRequest' 导入")
else:
    print("   ❌ 未找到 'VerifyPasswordRequest' 导入")

print("\n3. 检查 schemas.py 中的定义...")
schemas_path = os.path.join(backend_dir, 'schemas.py')
with open(schemas_path, 'r', encoding='utf-8') as f:
    schemas_content = f.read()

if 'class VerifyPasswordRequest' in schemas_content:
    print("   ✅ 找到 'VerifyPasswordRequest' 类定义")
else:
    print("   ❌ 未找到 'VerifyPasswordRequest' 类定义")

print("\n4. 检查 main.py 中的路由注册...")
main_path = os.path.join(backend_dir, 'main.py')
with open(main_path, 'r', encoding='utf-8') as f:
    main_content = f.read()

if 'include_router(auth_router' in main_content:
    print("   ✅ 找到 auth_router 注册")
else:
    print("   ❌ 未找到 auth_router 注册")

print("\n5. 检查 auth_router 的前缀...")
if 'prefix="/api"' in content:
    print("   ✅ auth_router 前缀设置为 '/api'")
else:
    print("   ⚠️ 未明确找到前缀设置为 '/api'")

print("\n" + "=" * 60)
print("总结")
print("=" * 60)
print("""
关键信息：
- 前端请求路径: /api/verify-password
- 后端 auth_router 前缀: /api
- 后端端点路径: /verify-password
- 完整路径: POST /api/verify-password

可能的问题：
1. 后端服务未重启，新添加的端点未生效
2. 后端代码有语法错误导致服务无法启动
3. 前端请求路径不正确

建议：
1. 重启后端服务（重要！）
2. 检查后端启动日志是否有错误
3. 访问 http://localhost:8000/docs 确认端点是否存在
""")
