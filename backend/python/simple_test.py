import urllib.request
import json

BASE_URL = 'http://localhost:8000'

def test_health():
    print('测试 1: 健康检查')
    print('-' * 40)
    try:
        req = urllib.request.Request(f'{BASE_URL}/')
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            print(f'状态码: {response.status}')
            print(f'响应: {data}')
            return True
    except Exception as e:
        print(f'错误: {e}')
        return False

def test_register():
    print()
    print('测试 2: 注册用户')
    print('-' * 40)
    
    test_user = {
        'username': 'test_user_999',
        'password': '123456',
        'confirm_password': '123456',
        'nickname': '测试用户'
    }
    
    print(f'请求: {test_user}')
    
    try:
        data = json.dumps(test_user).encode('utf-8')
        req = urllib.request.Request(
            f'{BASE_URL}/api/register',
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Content-Length': len(data)
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            print(f'状态码: {response.status}')
            print(f'响应: {json.dumps(result, ensure_ascii=False, indent=2)}')
            return response.status == 200
    except urllib.error.HTTPError as e:
        print(f'HTTP 错误: {e.code}')
        try:
            error_data = json.loads(e.read().decode())
            print(f'错误信息: {json.dumps(error_data, ensure_ascii=False, indent=2)}')
        except:
            pass
        return False
    except Exception as e:
        print(f'错误: {type(e).__name__}: {e}')
        return False

def test_login():
    print()
    print('测试 3: 登录用户')
    print('-' * 40)
    
    login_data = {
        'username': 'test_user_999',
        'password': '123456'
    }
    
    print(f'请求: {login_data}')
    
    try:
        data = json.dumps(login_data).encode('utf-8')
        req = urllib.request.Request(
            f'{BASE_URL}/api/login',
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Content-Length': len(data)
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            print(f'状态码: {response.status}')
            print(f'响应: {json.dumps(result, ensure_ascii=False, indent=2)}')
            return response.status == 200
    except urllib.error.HTTPError as e:
        print(f'HTTP 错误: {e.code}')
        try:
            error_data = json.loads(e.read().decode())
            print(f'错误信息: {json.dumps(error_data, ensure_ascii=False, indent=2)}')
        except:
            pass
        return False
    except Exception as e:
        print(f'错误: {type(e).__name__}: {e}')
        return False

if __name__ == '__main__':
    print('=' * 50)
    print('简单认证测试')
    print('=' * 50)
    
    results = {}
    
    results['健康检查'] = test_health()
    results['注册'] = test_register()
    results['登录'] = test_login()
    
    print()
    print('=' * 50)
    print('测试结果')
    print('=' * 50)
    
    all_passed = True
    for name, passed in results.items():
        status = 'PASS' if passed else 'FAIL'
        print(f'[{status}] {name}')
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print('所有测试通过！')
    else:
        print('部分测试失败。')
