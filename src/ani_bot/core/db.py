from sqlmodel import Session, create_engine


import os

database_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "anime.db")
# 确保目录存在
os.makedirs(os.path.dirname(database_path), exist_ok=True)
engine = create_engine(f"sqlite:///{database_path}")
