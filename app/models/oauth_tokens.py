from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
from app.database import Base


class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    user_id = Column(String, primary_key=True, nullable=False)
    provider = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)