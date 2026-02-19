from contextlib import asynccontextmanager, contextmanager
from sqlmodel import SQLModel, Session, create_engine


import os

database_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "anime.db")
# 确保目录存在
os.makedirs(os.path.dirname(database_path), exist_ok=True)
engine = create_engine(f"sqlite:///{database_path}")

@contextmanager
def session_scope():
    """
    非路由环境的会话上下文管理器
    自动处理 commit/rollback/close
    """
    db = Session(engine)
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

@asynccontextmanager
async def async_session_scope():
    """异步上下文管理器（适合 async 任务）"""
    db = Session(engine)
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """创建所有数据库表"""
    SQLModel.metadata.create_all(bind=engine)