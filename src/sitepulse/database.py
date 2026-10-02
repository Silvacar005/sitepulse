from __future__ import annotations

import os
from collections.abc import Generator
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker


DATABASE_URL = os.getenv("SITEPULSE_DATABASE_URL", "sqlite:///./sitepulse.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Website(Base):
    __tablename__ = "websites"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(2048), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    scans: Mapped[list["ScanRecord"]] = relationship(
        back_populates="website",
        cascade="all, delete-orphan",
    )


class ScanRecord(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(primary_key=True)
    website_id: Mapped[int] = mapped_column(ForeignKey("websites.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        index=True,
    )
    site_health: Mapped[int] = mapped_column(Integer)
    pages_scanned: Mapped[int] = mapped_column(Integer)
    total_issues: Mapped[int] = mapped_column(Integer)
    high_issues: Mapped[int] = mapped_column(Integer)
    medium_issues: Mapped[int] = mapped_column(Integer)
    low_issues: Mapped[int] = mapped_column(Integer)
    link_check_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    links_checked: Mapped[int] = mapped_column(Integer, default=0)
    broken_links_count: Mapped[int] = mapped_column(Integer, default=0)

    website: Mapped[Website] = relationship(back_populates="scans")
    pages: Mapped[list["PageRecord"]] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
        order_by="PageRecord.id",
    )
    crawl_errors: Mapped[list["CrawlErrorRecord"]] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
        order_by="CrawlErrorRecord.id",
    )
    broken_links: Mapped[list["BrokenLinkRecord"]] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
        order_by="BrokenLinkRecord.id",
    )


class PageRecord(Base):
    __tablename__ = "pages"

    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"), index=True)
    url: Mapped[str] = mapped_column(String(2048))
    score: Mapped[int] = mapped_column(Integer)
    status_code: Mapped[int] = mapped_column(Integer)
    response_time_ms: Mapped[int] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    h1_count: Mapped[int] = mapped_column(Integer)
    image_count: Mapped[int] = mapped_column(Integer)
    images_missing_alt: Mapped[int] = mapped_column(Integer)
    internal_link_count: Mapped[int] = mapped_column(Integer)
    external_link_count: Mapped[int] = mapped_column(Integer)

    scan: Mapped[ScanRecord] = relationship(back_populates="pages")
    issues: Mapped[list["IssueRecord"]] = relationship(
        back_populates="page",
        cascade="all, delete-orphan",
        order_by="IssueRecord.id",
    )


class IssueRecord(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(primary_key=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("pages.id"), index=True)
    severity: Mapped[str] = mapped_column(String(16))
    category: Mapped[str] = mapped_column(String(64))
    message: Mapped[str] = mapped_column(Text)

    page: Mapped[PageRecord] = relationship(back_populates="issues")


class CrawlErrorRecord(Base):
    __tablename__ = "crawl_errors"

    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"), index=True)
    url: Mapped[str] = mapped_column(String(2048))
    message: Mapped[str] = mapped_column(Text)

    scan: Mapped[ScanRecord] = relationship(back_populates="crawl_errors")


class BrokenLinkRecord(Base):
    __tablename__ = "broken_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"), index=True)
    url: Mapped[str] = mapped_column(String(2048))
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[int] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    scan: Mapped[ScanRecord] = relationship(back_populates="broken_links")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
