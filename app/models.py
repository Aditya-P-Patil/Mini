from sqlalchemy import UniqueConstraint
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Document(Base):
    __tablename__="documents"

    id: Mapped[int]=mapped_column(primary_key=True, index=True)
    filename: Mapped[str]=mapped_column(String(255), nullable=False)
    content_type: Mapped[str]=mapped_column(String(100), default="application/pdf")
    page_count: Mapped[int]=mapped_column(Integer, default=0)
    uploaded_at: Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    pages: Mapped[list["DocumentPage"]]=relationship(
        back_populates="document",
        cascade="all, delete-orphan"
    )


class DocumentPage(Base):
    __tablename__="document_pages"

    id: Mapped[int]=mapped_column(primary_key=True, index=True)
    document_id: Mapped[int]=mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    page_number: Mapped[int]=mapped_column(Integer, nullable=False)
    text: Mapped[str]=mapped_column(Text, nullable=False)

    document: Mapped["Document"]=relationship(back_populates="pages")


class DocumentChunk(Base):
    __tablename__="document_chunks"

    __table_args__=(
        UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunk_index"
        ),
    )

    id: Mapped[int]=mapped_column(primary_key=True, index=True)
    document_id: Mapped[int]=mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    page_number: Mapped[int]=mapped_column(Integer, nullable=False)
    chunk_index: Mapped[int]=mapped_column(Integer, nullable=False)
    text: Mapped[str]=mapped_column(Text, nullable=False)
