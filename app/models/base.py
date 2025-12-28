"""SQLAlchemy Base model with snowflake ID support."""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.utils.snowflake import generate_id


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class BaseModel(Base):
    """Base model with snowflake ID, timestamps and audit fields."""
    __abstract__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, default=generate_id, comment="主键(雪花算法)")
    create_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, comment="创建人ID")
    update_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, comment="更新人ID")
    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    remark: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, comment="备注")
