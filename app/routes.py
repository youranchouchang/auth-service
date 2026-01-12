from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.models import User, LoginHistory
from app.auth import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_token
from app.database import get_db
from datetime import datetime

router = APIRouter()

def validate_password(password: str):
    """验证密码是否符合要求"""
    if not password or len(password) < 6:
        return False, "密码长度至少6个字符"
    if len(password.encode("utf-8")) > 100:  # 限制密码长度
        return False, "密码过长"
    return True, ""

@router.post("/register")
async def register(user_data: dict, db: Session = Depends(get_db)):
    # 验证密码
    password = user_data.get("password", "")
    is_valid, message = validate_password(password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 检查邮箱是否已存在
    existing_user = db.query(User).filter(User.email == user_data.get("email")).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(password)
    new_user = User(
        email=user_data.get("email"),
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully", "user_id": new_user.id}

@router.post("/login")
async def login(request: Request, user_data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.get("email")).first()
    if not user or not verify_password(user_data.get("password"), user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # 记录登录历史
    user_agent = request.headers.get("user-agent", "")
    login_history = LoginHistory(
        user_id=user.id, 
        user_agent=user_agent, 
        login_time=datetime.utcnow()
    )
    db.add(login_history)
    db.commit()
    
    # 生成令牌
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
async def refresh_token(request: dict):
    refresh_token = request.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required"
        )
    
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    new_access_token = create_access_token(data={"sub": email})
    
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.get("/user/history")
async def get_login_history(db: Session = Depends(get_db)):
    # 简化实现：返回所有登录历史
    histories = db.query(LoginHistory).all()
    return {"history": [{"id": h.id, "user_id": h.user_id, "login_time": h.login_time.isoformat()} for h in histories]}

@router.post("/logout")
async def logout():
    # 在实际应用中，这里应该将令牌加入黑名单
    return {"message": "Logged out successfully"}