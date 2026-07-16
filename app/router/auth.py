import json
import os
from datetime import timezone
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from googleapiclient.discovery import build
from app.config import (
    GOOGLE_REDIRECT_URI,
    FRONTEND_URL
)
from app.service.auth_service import AuthService
from app.service.user_service import UserService

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

user_service = UserService()
auth_service = AuthService()
PKCE_VERIFIERS = {}
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


def build_auth_redirect_response(frontend_url: str, token_payload: dict, user_payload: dict):
    response = RedirectResponse(url=f"{frontend_url}/dashboard")
    response.set_cookie(
        key="auth_token",
        value=json.dumps(token_payload),
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    response.set_cookie(
        key="user",
        value=json.dumps(user_payload),
        httponly=False,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    return response


@router.get("/google/login")
async def google_login():
    try:
        flow = auth_service.create_flow()
    except HTTPException:
        raise

    code_verifier = auth_service.generate_code_verifier()
    code_challenge = auth_service.generate_code_challenge(code_verifier)

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
        flow = auth_service.create_flow()

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

        user = user_service.create_user(
            user_info.get("email"),
            user_info.get("name")
        )

        print("\n========== USER ==========")
        print(user)
        print("========== USER ==========\n")
        print("credentials:", credentials)

        expires_at = credentials.expiry
        if expires_at is not None and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        print("expires_at:", expires_at)

        token = auth_service.create_token(
            email=user_info.get("email"),
            refresh_token=credentials.refresh_token,
            access_token=credentials.token,
            expires_at=expires_at,
        )

        print(f"Token created: {token}")

        token_payload = {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expires_at": expires_at.isoformat() if expires_at else None,
        }
        user_payload = {
            "id": str(user.id) if user else None,
            "email": user.email if user else user_info.get("email"),
            "name": user.name if user else user_info.get("name"),
        }

        return build_auth_redirect_response(
            frontend_url=FRONTEND_URL,
            token_payload=token_payload,
            user_payload=user_payload,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        )
