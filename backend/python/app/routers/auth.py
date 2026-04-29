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

auth_router = APIRouter(tags=["认证"])


def get_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    password_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    
    hash_bytes = hashlib.pbkdf2_hmac(
        'sha256',
        password_bytes,
        salt_bytes,
        100000,
        dklen=32
    )
    
    hash_hex = base64.b64encode(hash_bytes).decode('utf-8')
    return f"pbkdf2_sha256$100000${salt}${hash_hex}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password or '$' not in hashed_password:
        return False
    
    parts = hashed_password.split('$')
    if len(parts) != 4:
        return False
    
    algorithm, iterations_str, salt, stored_hash = parts
    
    try:
        iterations = int(iterations_str)
    except ValueError:
        return False
    
    password_bytes = plain_password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    
    hash_bytes = hashlib.pbkdf2_hmac(
        'sha256',
        password_bytes,
        salt_bytes,
        iterations,
        dklen=32
    )
    
    computed_hash = base64.b64encode(hash_bytes).decode('utf-8')
    
    return secrets.compare_digest(computed_hash, stored_hash)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, username: str, password: str, nickname: Optional[str] = None) -> User:
    user = User(
        id=str(uuid.uuid4()),
        username=username,
        password_hash=get_password_hash(password),
        nickname=nickname or username,
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


class AuthError(Exception):
    def __init__(self, message: str, error_type: str):
        self.message = message
        self.error_type = error_type


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User:
    user = await get_user_by_username(db, username)
    if not user:
        raise AuthError("账号不存在", "user_not_found")
    if not verify_password(password, user.password_hash):
        raise AuthError("密码错误", "wrong_password")
    return user


@auth_router.post("/register", response_model=ApiResponse[UserResponse])
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_async_session)
):
    existing_user = await get_user_by_username(db, request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    user = await create_user(
        db=db,
        username=request.username,
        password=request.password,
        nickname=request.nickname
    )
    
    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(user),
        message="注册成功"
    )


@auth_router.post("/login", response_model=ApiResponse[LoginResponse])
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        user = await authenticate_user(db, request.username, request.password)
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    user.last_login_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return ApiResponse(
        success=True,
        data=LoginResponse(
            accessToken=access_token,
            tokenType="bearer",
            user=UserResponse.model_validate(user)
        ),
        message="登录成功"
    )


@auth_router.post("/change-password", response_model=ApiResponse[dict])
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )

    current_user.password_hash = get_password_hash(request.new_password)
    await db.commit()

    return ApiResponse(
        success=True,
        data={},
        message="密码修改成功"
    )


@auth_router.post("/verify-password", response_model=ApiResponse[dict])
async def verify_user_password(
    request: VerifyPasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    if not verify_password(request.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码错误"
        )

    return ApiResponse(
        success=True,
        data={},
        message="密码验证成功"
    )
