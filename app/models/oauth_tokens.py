from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from sqlalchemy.sql import text

class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    user_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    email = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)