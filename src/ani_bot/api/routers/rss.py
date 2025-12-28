from typing import Any
from fastapi import APIRouter, Depends
from ani_bot.api.deps import SessionDep
from ani_bot.db.models import RSSItem

router = APIRouter(prefix="/rss", tags=["rss"])



@router.get(
    path="",
    dependencies=[Depends(SessionDep)],
    response_model=list[RSSItem]
)
def get_rss(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    count_statement = select(func.count()).select_from(RSSItem)
    count = session.exec(count_statement).one()

    statement = select(RSSItem).offset(skip).limit(limit)
    rssItems = session.exec(statement).all()

    return RSSItemPublic(data=rssItems, count=count)
