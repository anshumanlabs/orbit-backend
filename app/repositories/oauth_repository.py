from uuid import UUID
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models.oauth_tokens import OAuthToken

class OAuthTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert(self, user_id: str, provider: str, refresh_token: str, expires_at: datetime) -> OAuthToken:
        token = self.db.query(OAuthToken).filter(OAuthToken.user_id == user_id).first()
        if token:
            token.provider = provider
            token.refresh_token = refresh_token
            token.expires_at = expires_at
        else:
            token = OAuthToken(
                user_id=user_id,
                provider=provider,
                refresh_token=refresh_token,
                expires_at=expires_at,
            )
            self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def get_by_user_id(self, user_id: str) -> Optional[OAuthToken]:
        return self.db.query(OAuthToken).filter(OAuthToken.user_id == user_id).first()

    def delete(self, user_id: str) -> None:
        token = self.db.query(OAuthToken).filter(OAuthToken.user_id == user_id).first()
        if token:
            self.db.delete(token)
            self.db.commit()