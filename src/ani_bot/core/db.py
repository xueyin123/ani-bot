from sqlmodel import Session, create_engine


database_path = "src/ani_bot/resources/anime.db"
engine = create_engine(f"sqlite:///{database_path}")
