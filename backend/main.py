"""
FastAPI主入口文件
人生观调研APP后端服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import auth, survey, admin

# 创建FastAPI应用
app = FastAPI(
    title="人生观调研APP API",
    description="人生观线上调研系统的后端API服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(survey.router)
app.include_router(admin.router)


@app.on_event("startup")
def startup_event():
    """应用启动时初始化数据库"""
    init_db()
    print("数据库初始化完成")


@app.get("/", summary="服务健康检查")
def root():
    """服务根路径，返回API信息"""
    return {
        "name": "人生观调研APP API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", summary="健康检查")
def health_check():
    """健康检查接口"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# ===== 静态文件服务（后台管理系统） =====
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

ADMIN_DIST = os.environ.get("ADMIN_DIST", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "admin", "dist"))
if os.path.exists(ADMIN_DIST):
    # 静态资源
    app.mount("/admin-assets", StaticFiles(directory=os.path.join(ADMIN_DIST, "assets")), name="admin-assets")
    
    @app.get("/admin/{path:path}")
    async def serve_admin(path: str):
        """服务后台管理系统的所有路由"""
        file_path = os.path.join(ADMIN_DIST, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(ADMIN_DIST, "index.html"))
    
    @app.get("/admin")
    async def serve_admin_index():
        """后台管理系统首页"""
        return FileResponse(os.path.join(ADMIN_DIST, "index.html"))
