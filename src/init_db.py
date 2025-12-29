from sqlmodel import SQLModel, create_engine
from ani_bot.core.db import database_path, engine
from ani_bot.db.models import *

def init_db():
    """初始化数据库，创建所有表"""
    print(f"初始化数据库: {database_path}")
    SQLModel.metadata.create_all(engine)
    print("数据库初始化完成")

if __name__ == "__main__":
    init_db()