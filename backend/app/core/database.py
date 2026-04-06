"""Database configuration."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


@lru_cache
def get_database_url():
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url


@lru_cache
def get_engine():
    return create_engine(get_database_url())


@lru_cache
def get_session_factory():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def ensure_database_schema():
    with get_engine().begin() as connection:
        connection.execute(text("ALTER TABLE IF EXISTS anomalies ADD COLUMN IF NOT EXISTS severity VARCHAR(20)"))
        connection.execute(
            text(
                """
                UPDATE anomalies
                SET severity = CASE
                    WHEN flag_type = 'Low Yield' THEN 'Medium'
                    ELSE 'High'
                END
                WHERE severity IS NULL OR severity = ''
                """
            )
        )
        connection.execute(text("ALTER TABLE IF EXISTS anomalies ALTER COLUMN severity SET NOT NULL"))


def get_db():
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()
