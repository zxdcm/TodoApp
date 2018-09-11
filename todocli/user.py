from sqlalchemy import (
    Column,
    String,
)

from todolib.models import BaseModel


class User(BaseModel):
    __tablename__ = 'users'
    username = Column(String, primary_key=True)

    def __init__(self, username):
        self.username = username

    def __str__(self):
        return self.username
