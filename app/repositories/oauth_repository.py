from datetime import datetime
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.oauth_tokens import OAuthToken

class OAuthTokenRepository:
    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()

    def upsert(self, user_id: str, email:str, provider: str, refresh_token: str, expires_at: datetime) -> Optional[OAuthToken]:
        try:
            token = self.db.query(OAuthToken).filter(OAuthToken.user_id == user_id).first()
            if token:
                token.email = email
                token.provider = provider
                token.refresh_token = refresh_token
                token.expires_at = expires_at
            else:
                token = OAuthToken(
                    user_id=user_id,
                    email=email,
                    provider=provider,
                    refresh_token=refresh_token,
                    expires_at=expires_at,
                )
                self.db.add(token)
            self.db.commit()
            self.db.refresh(token)
            return token
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def get_by_email_id(self, email_id: str) -> Optional[OAuthToken]:
        return self.db.query(OAuthToken).filter(OAuthToken.email == email_id).first()

    def delete(self, user_id: str) -> None:
        token = self.db.query(OAuthToken).filter(OAuthToken.user_id == user_id).first()
        if token:
            self.db.delete(token)
            self.db.commit()