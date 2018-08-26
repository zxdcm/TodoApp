from sqlalchemy import (
    Column,
    String,
)

from todolib.models import Base


class User(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=True)

    def __init__(self, username):
        self.username = username

    def __str__(self):
        return self.username
