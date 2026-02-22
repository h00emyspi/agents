import asyncio
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config import settings

Base = declarative_base()


class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    moltbook_id = Column(String, unique=True)
    title = Column(String(500))
    content = Column(Text)
    author_name = Column(String(200))
    created_at = Column(DateTime)
    collected_at = Column(DateTime, default=datetime.utcnow)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)


class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True)
    moltbook_id = Column(String)
    post_id = Column(Integer)
    direction = Column(String(10))
    collected_at = Column(DateTime, default=datetime.utcnow)


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True)
    moltbook_id = Column(String)
    post_id = Column(Integer)
    content = Column(Text)
    author_name = Column(String(200))
    created_at = Column(DateTime)


class AgentStats(Base):
    __tablename__ = "agent_stats"
    
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(200), unique=True)
    karma = Column(Float, default=0)
    posts_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)


class Database:
    def __init__(self):
        self.engine = create_engine(settings.database_url.replace("sqlite:///", "sqlite:////"))
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_post(self, moltbook_id: str, title: str, content: str, author: str, created_at: str, votes: Dict[str, int]) -> Post:
        session = self.Session()
        try:
            post = Post(
                moltbook_id=moltbook_id,
                title=title,
                content=content,
                author_name=author,
                created_at=datetime.fromisoformat(created_at.replace("Z", "+00:00")),
                upvotes=votes.get("up", 0),
                downvotes=votes.get("down", 0)
            )
            session.merge(post)
            session.commit()
            return post
        finally:
            session.close()
    
    def get_top_posts(self, limit: int = 10) -> List[Post]:
        session = self.Session()
        try:
            return session.query(Post).order_by(
                (Post.upvotes - Post.downvotes).desc()
            ).limit(limit).all()
        finally:
            session.close()
    
    def get_recent_posts(self, limit: int = 20) -> List[Post]:
        session = self.Session()
        try:
            return session.query(Post).order_by(
                Post.collected_at.desc()
            ).limit(limit).all()
        finally:
            session.close()
    
    def update_agent_stats(self, agent_name: str, karma: float, posts_count: int):
        session = self.Session()
        try:
            stats = AgentStats(
                agent_name=agent_name,
                karma=karma,
                posts_count=posts_count,
                last_updated=datetime.utcnow()
            )
            session.merge(stats)
            session.commit()
        finally:
            session.close()
    
    def get_agent_stats(self, agent_name: str) -> AgentStats:
        session = self.Session()
        try:
            return session.query(AgentStats).filter_by(agent_name=agent_name).first()
        finally:
            session.close()


db = Database()
