import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing auth.py imports...")
try:
    from fastapi import APIRouter, Depends, HTTPException, status
    from fastapi.responses import JSONResponse
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from datetime import datetime, timedelta
    from typing import Optional
    import uuid
    import hashlib
    import base64
    import secrets

    from jose import JWTError, jwt

    from app.database import get_async_session
    from app.config import settings
    from app.models import User
    from app.schemas import (
        ApiResponse,
        UserRegisterRequest,
        UserLoginRequest,
        UserResponse,
        LoginResponse,
        ChangePasswordRequest,
        VerifyPasswordRequest
    )
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting main.py imports...")
try:
    from app.main import app
    print("✅ Main app imported successfully")
    
    # 打印所有路由
    print("\nRegistered routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  {route.methods if hasattr(route, 'methods') else 'GET'} {route.path}")
except Exception as e:
    print(f"❌ Main app import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
