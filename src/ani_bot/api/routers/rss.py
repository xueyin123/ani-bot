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


@router.post(
    path="",
    response_model=RSSFeed
)
def create_rss(session: SessionDep, rss_feed: RSSFeed) -> RSSFeed:
    feed = crud.create_rss_feed(session, rss_feed)
    return feed

@router.delete(
    path="/{rss_id}",
    response_model=dict
)
def delete_rss(session: SessionDep, rss_id: int) -> Any:
    crud.delete_rss_feed(session, rss_id)
    return {"detail": "RSS feed deleted successfully."}

@router.put(
    path="/{rss_id}",
    response_model=RSSFeed
)
def update_rss(session: SessionDep, rss_id: int, rss_feed: RSSFeed) -> RSSFeed:
    update_feed = crud.update_rss_feed(session, rss_id, rss_feed)
    if not update_feed:
        raise HTTPException(status_code=404, detail="RSS feed not found.")
    return update_feed