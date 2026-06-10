"""
认证路由模块
处理用户登录、注册等认证相关接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import LoginRequest, RegisterRequest, AuthResponse, UserResponse, AdminLoginRequest
from auth import create_access_token, get_current_user, verify_password
import random

router = APIRouter(prefix="/api/auth", tags=["认证"])

# 模拟验证码存储（生产环境应使用Redis）
VERIFICATION_CODES = {}


def generate_code() -> str:
    """生成6位验证码"""
    return "123456"  # 写死的验证码


def send_verification_code(phone: str, code: str):
    """发送验证码（模拟）"""
    # 实际项目中这里应该调用短信服务
    print(f"[模拟短信] 向 {phone} 发送验证码: {code}")
    VERIFICATION_CODES[phone] = code


@router.post("/send-code", summary="发送验证码")
def send_code(phone: str):
    """发送登录验证码"""
    if len(phone) != 11 or not phone.isdigit():
        raise HTTPException(status_code=400, detail="手机号格式不正确")
    
    code = generate_code()
    send_verification_code(phone, code)
    return {"message": "验证码已发送", "code": code}  # 开发模式下返回验证码


@router.post("/login", response_model=AuthResponse, summary="用户登录")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    # 验证验证码（使用写死的123456）
    if request.code != "123456":
        raise HTTPException(status_code=400, detail="验证码错误")
    
    # 查找或创建用户
    user = db.query(User).filter(User.phone == request.phone).first()
    if not user:
        # 自动注册
        user = User(phone=request.phone, nickname=f"用户{request.phone[-4:]}")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # 生成token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return AuthResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/register", response_model=AuthResponse, summary="用户注册")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查手机号是否已注册
    existing_user = db.query(User).filter(User.phone == request.phone).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="手机号已注册")
    
    # 创建用户
    user = User(
        phone=request.phone,
        nickname=request.nickname or f"用户{request.phone[-4:]}"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 生成token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return AuthResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/admin/login", response_model=AuthResponse, summary="管理员登录")
def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    """管理员登录（用户名密码）"""
    # 查找管理员用户
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 验证密码
    if not user.password_hash or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 检查是否为管理员
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="无管理员权限")
    
    # 生成token
    access_token = create_access_token(data={"sub": str(user.id), "is_admin": True})
    
    return AuthResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return UserResponse.model_validate(current_user)
