from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session
from ani_bot.core.db import engine

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

# 正确定义类型别名
SessionDep = Annotated[Session, Depends(get_db)]