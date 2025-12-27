from fastapi import APIRouter

router = APIRouter(prefix="/rss", tags=["rss"])



@router.get(
    path="", response_model=list[RSSItem]
)
def get_rss():
    with RSSEngine() as engine:
        return engine.rss.search_all()

@router.get(
    path="/{rss_id}", response_model=RSSItem
)
def get_rss_item(rss_id: int):
    with RSSEngine() as engine:
        return engine.rss.search_by_id(rss_id)

@router.post(
    path="/add", response_model=RSSItem
)
def add_rss_item(rss_item: RSSItem):
    with RSSEngine() as engine:
        return engine.rss.add(rss_item)

@router.delete(
    path="/{rss_id}", response_model=RSSItem
)
def delete_rss_item(rss_id: int):
    with RSSEngine() as engine:
        return engine.rss.delete(rss_id)

@router.put(
    path="/{rss_id}", response_model=RSSItem
)
def update_rss_item(rss_id: int, rss_item: RSSItem):
    with RSSEngine() as engine:
        return engine.rss.update(rss_id, rss_item)

