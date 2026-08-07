from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings
from sqlalchemy.orm import DeclarativeBase

engine = create_engine(
    settings.database_url,
    echo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

class Base(DeclarativeBase):
    pass

