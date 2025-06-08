from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Chat(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    room: Mapped[str] = mapped_column(db.String(50), nullable=False)
    date: Mapped[str] = mapped_column(db.String(50), nullable=False)
    time: Mapped[str] = mapped_column(db.String(50), nullable=False)
    username: Mapped[str] = mapped_column(db.String(50), nullable=False)
    message: Mapped[str] = mapped_column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "room": self.room,
            "date": self.date,
            "time": self.time,
            "username": self.username,
            "message": self.message
        }
