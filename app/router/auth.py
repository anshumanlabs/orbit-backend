import os
import secrets
import hashlib
import base64
from pathlib import Path

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from app.config import (
    GOOGLE_REDIRECT_URI,
    FRONTEND_URL
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly"
]

CREDENTIALS_PATH = Path(__file__).resolve().parent.parent.parent / "credentials.json"

PKCE_VERIFIERS = {}


def generate_code_verifier():
    return secrets.token_urlsafe(64)


def generate_code_challenge(verifier):
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


def create_flow():
    if not CREDENTIALS_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"credentials.json not found at {CREDENTIALS_PATH}"
        )

    flow = Flow.from_client_secrets_file(
        str(CREDENTIALS_PATH),
        scopes=SCOPES
    )

    flow.redirect_uri = GOOGLE_REDIRECT_URI

    return flow


@router.get("/google/login")
async def google_login():
    try:
        flow = create_flow()
    except HTTPException:
        raise

    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        code_challenge=code_challenge,
        code_challenge_method="S256"
    )

    PKCE_VERIFIERS[state] = code_verifier

    return RedirectResponse(url=authorization_url)


@router.get("/google/callback")
async def google_callback(request: Request):
    error = request.query_params.get("error")
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"OAuth error: {error}"
        )

    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code:
        raise HTTPException(
            status_code=400,
            detail="Missing authorization code in callback"
        )

    if not state or state not in PKCE_VERIFIERS:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired state"
        )

    code_verifier = PKCE_VERIFIERS.pop(state)

    try:
        flow = create_flow()

        flow.fetch_token(
            authorization_response=str(request.url),
            code_verifier=code_verifier
        )

        credentials = flow.credentials

        oauth_service = build(
            "oauth2",
            "v2",
            credentials=credentials
        )

        user_info = (
            oauth_service.userinfo()
            .get()
            .execute()
        )

        gmail_service = build(
            "gmail",
            "v1",
            credentials=credentials
        )

        profile = (
            gmail_service.users()
            .getProfile(userId="me")
            .execute()
        )

        print("\n========== USER INFO ==========")
        print(user_info)

        print("\n========== GMAIL PROFILE ==========")
        print(profile)

        print("\n========== TOKENS ==========")
        print("Access Token:", credentials.token)
        print("Refresh Token:", credentials.refresh_token)

        return RedirectResponse(
            url=f"{FRONTEND_URL}/dashboard"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        )
