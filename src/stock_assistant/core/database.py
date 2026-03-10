"""数据库引擎和会话管理"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from stock_assistant.core.config import get_settings

_engine = None
_session_factory = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        db_url = settings.database.url
        # 确保SQLite目录存在
        if "sqlite" in db_url:
            db_path = db_url.replace("sqlite:///", "")
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(db_url, echo=False)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine())
    return _session_factory


def get_session() -> Session:
    return get_session_factory()()


def init_db():
    """创建所有表"""
    from stock_assistant.core.models import Base
    Base.metadata.create_all(get_engine())
