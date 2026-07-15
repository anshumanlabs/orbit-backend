from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.oauth_tokens import OAuthToken

class OAuthTokenRepository:
    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()

    def upsert(
        self,
        email: str,
        provider: str,
        refresh_token: str,
        access_token: str,
        expires_at: datetime,
    ) -> Optional[OAuthToken]:
            token = self.db.query(OAuthToken).filter(OAuthToken.email == email).first()
            if token:
                token.email = email
                token.provider = provider
                token.refresh_token = refresh_token
                token.access_token = access_token
                token.expires_at = expires_at
            else:
                token = OAuthToken(
                    email=email,
                    provider=provider,
                    refresh_token=refresh_token,
                    access_token=access_token,
                    expires_at=expires_at,
                )            
            self.db.add(token)
            self.db.commit()
            self.db.refresh(token)
            return token

    def get_by_email_id(self, email_id: str) -> Optional[OAuthToken]:
        return self.db.query(OAuthToken).filter(OAuthToken.email == email_id).first()

    def delete(self, user_id: str) -> None:
        token = self.db.query(OAuthToken).filter(OAuthToken.user_id == user_id).first()
        if token:
            self.db.delete(token)
            self.db.commit()