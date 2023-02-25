from typing import List
from typing import Optional
from sqlalchemy import (
    String,
    Column,
    Integer,
    String,
    DateTime,
    func,
    Text,
    create_engine,
    select,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session


class Base(DeclarativeBase):
    pass


class Raw_Data(Base):
    __tablename__ = "raw_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    news_creation_date = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    remarks: Mapped[str] = mapped_column(Text)
    created_at = mapped_column(DateTime, default=func.now())


if __name__ == "__main__":
    engine = create_engine(
        "postgresql://postgres:Iamalextay96@192.168.1.3:5433/nlp", echo=True
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        spongebob = Raw_Data(
            source="malaysiakini",
            content="Spongebob Squarepants",
            remarks="spongebob@sqlalchemy.org",
            title="title",
            news_creation_date="aa",
        )

        session.add_all([spongebob])
        session.commit()
        stmt = select(Raw_Data).where(Raw_Data.source.in_(["malaysiakini", "sandy"]))
        queryResults = session.scalars(stmt).all()
        print(queryResults)
