from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func
from ani_bot.api.deps import SessionDep
from ani_bot.db.models import RSSFeed
from ani_bot.db import crud
from datetime import datetime, timezone

router = APIRouter(prefix="/rss", tags=["rss"])


@router.get(
    path="",
    response_model=dict  
)
def get_rss(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    rss_items = crud.get_rss_feeds(session, skip=skip, limit=limit)
    count_statement = select(func.count()).select_from(RSSFeed)
    count = session.exec(count_statement).one()
    
    return {"data": rss_items, "count": count}