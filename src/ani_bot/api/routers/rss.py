from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func
from ani_bot.api.deps import SessionDep
from ani_bot.db.models import RSSItem, RSSItemPublic
from ani_bot.db import crud
from datetime import datetime

router = APIRouter(prefix="/rss", tags=["rss"])


@router.get(
    path="",
    response_model=dict  
)
def get_rss(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    rss_items = crud.get_rss_items(session, skip=skip, limit=limit)
    count_statement = select(func.count()).select_from(RSSItem)
    count = session.exec(count_statement).one()
    
    return {"data": rss_items, "count": count}


@router.post(
    path="",
    response_model=RSSItem
)
def create_rss(session: SessionDep, rss_item: RSSItem) -> Any:
    # 设置默认时间戳
    if not rss_item.created_at:
        rss_item.created_at = datetime.utcnow()
    if not rss_item.updated_at:
        rss_item.updated_at = datetime.utcnow()
    return crud.create_rss_item(session, rss_item)

@router.get(
    path="/{rss_id}",
    response_model=RSSItem
)
def get_rss_by_id(session: SessionDep, rss_id: int) -> Any:
    rss_item = crud.get_rss_item(session, rss_id)
    if not rss_item:
        raise HTTPException(status_code=404, detail="RSS item not found")
    return rss_item


@router.put(
    path="/{rss_id}",
    response_model=RSSItem
)
def update_rss(session: SessionDep, rss_id: int, rss_item: RSSItem) -> Any:
    existing_rss = crud.get_rss_item(session, rss_id)
    if not existing_rss:
        raise HTTPException(status_code=404, detail="RSS item not found")
    
    return crud.update_rss_item(session, rss_id, rss_item)


@router.delete(
    path="/{rss_id}",
    response_model=RSSItem
)
def delete_rss(session: SessionDep, rss_id: int) -> Any:
    rss_item = crud.get_rss_item(session, rss_id)
    if not rss_item:
        raise HTTPException(status_code=404, detail="RSS item not found")
    
    return crud.delete_rss_item(session, rss_id)