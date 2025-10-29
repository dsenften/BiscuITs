from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000))
    priority = Column(Integer, default=1)  # 1 = highest, 5 = lowest
    category = Column(String(50))
    due_date = Column(DateTime)
    is_completed = Column(Boolean, default=False)
    completion_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = relationship("Tag", secondary="todo_tags", back_populates="todos")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)
    todos = relationship("Todo", secondary="todo_tags", back_populates="tags")


class TodoTag(Base):
    __tablename__ = "todo_tags"

    todo_id = Column(Integer, ForeignKey("todos.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)


# Pydantic Models for API


class TagCreate(BaseModel):
    name: str


class TagOut(TagCreate):
    id: int

    class Config:
        from_attributes = True


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 1
    category: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[TagCreate]] = None


class TodoOut(TodoCreate):
    id: int
    is_completed: bool
    completion_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    tags: Optional[List[TagOut]] = None

    class Config:
        from_attributes = True
