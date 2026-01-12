from fastapi import FastAPI
from app.database import create_tables
from app import routes

# 创建FastAPI应用
app = FastAPI(
    title="Auth Service API",
    description="用户认证和授权服务",
    version="1.0.0"
)

# 启动时创建数据库表
@app.on_event("startup")
def on_startup():
    create_tables()
    print("数据库表初始化完成")

# 包含认证路由
app.include_router(routes.router, prefix="/api/v1", tags=["authentication"])

@app.get("/")
def read_root():
    return {"message": "Auth Service is running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
