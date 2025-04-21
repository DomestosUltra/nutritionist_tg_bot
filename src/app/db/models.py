from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from src.app.db.base import Base


class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    username = Column(String, nullable=True)
    user_query = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<UserInteraction(id={self.id}, user_id={self.user_id})>"
