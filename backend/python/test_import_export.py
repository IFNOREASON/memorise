import asyncio
import httpx
import pandas as pd
from io import BytesIO
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

API_BASE_URL = "http://localhost:8000/api"

# 测试用户凭据 - 需要先登录获取token
TEST_USERNAME = "test"
TEST_PASSWORD = "test123"


async def test_api():
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. 先登录获取token
        print("1. 尝试登录获取token...")
        try:
            login_response = await client.post(
                f"{API_BASE_URL}/login",
                json={"username": TEST_USERNAME, "password": TEST_PASSWORD}
            )
            print(f"登录响应状态: {login_response.status_code}")
            if login_response.status_code == 200:
                login_data = login_response.json()
                print(f"登录响应: {login_data}")
                if login_data.get('success') and login_data.get('data'):
                    token = login_data['data'].get('access_token')
                    print(f"获取到token: {token[:50]}...")
                    
                    # 2. 获取用户的家族信息
                    print("\n2. 获取用户家族信息...")
                    headers = {"Authorization": f"Bearer {token}"}
                    family_response = await client.get(f"{API_BASE_URL}/family", headers=headers)
                    print(f"获取家族信息状态: {family_response.status_code}")
                    family_data = family_response.json()
                    print(f"家族信息响应: {family_data}")
                    
                    if family_data.get('success') and family_data.get('data'):
                        family_id = family_data['data']['family']['id']
                        headers["X-Family-Id"] = family_id
                        print(f"当前家族ID: {family_id}")
                        
                        # 3. 测试导入预览接口
                        print("\n3. 测试导入预览接口...")
                        test_file_path = os.path.join(os.path.dirname(__file__), 'test_data', '家族成员测试数据.csv')
                        if os.path.exists(test_file_path):
                            with open(test_file_path, 'rb') as f:
                                files = {'file': ('家族成员测试数据.csv', f, 'text/csv')}
                                preview_response = await client.post(
                                    f"{API_BASE_URL}/family/import/preview",
                                    files=files,
                                    headers=headers
                                )
                                print(f"导入预览状态: {preview_response.status_code}")
                                preview_data = preview_response.json()
                                print(f"导入预览响应: {preview_data}")
                                
                                if preview_response.status_code == 200 and preview_data.get('success'):
                                    print(f"成功解析 {len(preview_data['data']['preview'])} 条数据")
                                    
                                    # 4. 测试实际导入接口
                                    print("\n4. 测试实际导入接口...")
                                    with open(test_file_path, 'rb') as f2:
                                        files2 = {'file': ('家族成员测试数据.csv', f2, 'text/csv')}
                                        import_response = await client.post(
                                            f"{API_BASE_URL}/family/import",
                                            files=files2,
                                            headers=headers
                                        )
                                        print(f"导入状态: {import_response.status_code}")
                                        import_data = import_response.json()
                                        print(f"导入响应: {import_data}")
                                        
                                        # 5. 测试导出Excel
                                        print("\n5. 测试导出Excel...")
                                        export_xlsx_response = await client.get(
                                            f"{API_BASE_URL}/family/export?format=xlsx",
                                            headers=headers
                                        )
                                        print(f"导出Excel状态: {export_xlsx_response.status_code}")
                                        
                                        if export_xlsx_response.status_code == 200:
                                            output_path = os.path.join(os.path.dirname(__file__), 'test_data', '导出测试.xlsx')
                                            with open(output_path, 'wb') as f:
                                                f.write(export_xlsx_response.content)
                                            print(f"Excel导出成功，保存到: {output_path}")
                                            
                                            # 验证导出文件可以读取
                                            df = pd.read_excel(BytesIO(export_xlsx_response.content))
                                            print(f"导出Excel包含 {len(df)} 条数据")
                                            print(f"列名: {list(df.columns)}")
                                            
                                            # 6. 测试导出CSV
                                            print("\n6. 测试导出CSV...")
                                            export_csv_response = await client.get(
                                                f"{API_BASE_URL}/family/export?format=csv",
                                                headers=headers
                                            )
                                            print(f"导出CSV状态: {export_csv_response.status_code}")
                                            
                                            if export_csv_response.status_code == 200:
                                                csv_path = os.path.join(os.path.dirname(__file__), 'test_data', '导出测试.csv')
                                                with open(csv_path, 'wb') as f:
                                                    f.write(export_csv_response.content)
                                                print(f"CSV导出成功，保存到: {csv_path}")
                                                
                                                # 验证导出文件可以读取
                                                df_csv = pd.read_csv(BytesIO(export_csv_response.content), encoding='utf-8-sig')
                                                print(f"导出CSV包含 {len(df_csv)} 条数据")
                                                
                                                # 7. 测试重复导入
                                                print("\n7. 测试重复导入（验证重复检测）...")
                                                with open(test_file_path, 'rb') as f3:
                                                    files3 = {'file': ('家族成员测试数据.csv', f3, 'text/csv')}
                                                    repeat_response = await client.post(
                                                        f"{API_BASE_URL}/family/import",
                                                        files=files3,
                                                        headers=headers
                                                    )
                                                    print(f"重复导入状态: {repeat_response.status_code}")
                                                    if repeat_response.status_code == 200:
                                                        repeat_data = repeat_response.json()
                                                        print(f"重复导入响应: {repeat_data}")
                else:
                    print("登录成功但未获取到有效数据结构")
            else:
                print(f"登录失败: {login_response.text}")
        except Exception as e:
            print(f"测试过程出错: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("族谱导入导出功能测试")
    print("=" * 60)
    asyncio.run(test_api())
