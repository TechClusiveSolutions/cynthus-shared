from uuid import UUID

from sqlalchemy import String, create_engine
from sqlalchemy.orm import Mapped, Session, mapped_column

from cynthus.model import Base


class Widget(Base):
    __tablename__ = 'widgets_for_base_test'

    name: Mapped[str] = mapped_column(String)


def test_the_id_is_none_until_the_insert_generates_it():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine, tables=[Widget.__table__])

    with Session(engine) as session:
        widget = Widget(name='a')

        assert widget.id is None

        session.add(widget)
        session.flush()

        assert isinstance(widget.id, UUID)


def test_an_id_given_by_the_caller_is_kept():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine, tables=[Widget.__table__])
    given = UUID(int=7)

    with Session(engine) as session:
        session.add(Widget(id=given, name='b'))
        session.flush()

        assert session.get(Widget, given).name == 'b'
