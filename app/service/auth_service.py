import os
import secrets
import hashlib
import base64
from datetime import datetime, timedelta

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from fastapi import HTTPException
from google_auth_oauthlib.flow import Flow

from app.config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
)
from app.repositories.oauth_repository import OAuthTokenRepository

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly"
]

CLIENT_CONFIG = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}


class AuthService:
    def __init__(self):
        self.oauth_token_repository = OAuthTokenRepository()

    def generate_code_verifier(self):
        return secrets.token_urlsafe(64)

    def generate_code_challenge(self, verifier):
        digest = hashlib.sha256(verifier.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")

    def create_flow(self):
        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            raise HTTPException(
                status_code=500,
                detail="Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET environment variables"
            )

        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES
        )

        flow.redirect_uri = GOOGLE_REDIRECT_URI

        return flow

    def create_token(
        self,
        email: str,
        refresh_token: str,
        access_token: str | None = None,
        expires_in: int | None = None,
        user_id: str | None = None,
        expires_at: datetime | None = None,
    ):
        try:
            if expires_at is None:
                if expires_in is not None:
                    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                else:
                    expires_at = datetime.utcnow()

            if user_id is None:
                user_id = email

            return self.oauth_token_repository.upsert(
                user_id=user_id,
                email=email,
                provider="google",
                refresh_token=refresh_token,
                expires_at=expires_at,
            )
        except Exception:
            return None