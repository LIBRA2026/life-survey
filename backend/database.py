"""
数据库配置文件
使用SQLite数据库，支持快速切换到PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 数据库路径 - 优先使用环境变量指定的持久化目录（Render等平台）
DATA_DIR = os.environ.get("DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'life_survey.db')}"

print(f"[数据库] 使用数据库文件: {DATABASE_URL}")

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite特定配置
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础模型
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)
    
    # 确保管理员账户存在
    from models import User
    from auth import get_password_hash
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == 'admin').first()
        if not admin:
            admin = User(
                phone='13800000000',
                username='admin',
                nickname='管理员',
                password_hash=get_password_hash('admin'),
                is_admin=1
            )
            db.add(admin)
            db.commit()
            print("[初始化] 管理员账户创建成功 (admin/admin)")
        else:
            print("[初始化] 管理员账户已存在")
    except Exception as e:
        print(f"[初始化] 管理员账户检查失败: {e}")
        db.rollback()
    finally:
        db.close()
