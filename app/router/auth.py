import os
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

        auth_service.create_token(
            email="gmail",
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            expires_in=credentials.expiry.timestamp()
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
