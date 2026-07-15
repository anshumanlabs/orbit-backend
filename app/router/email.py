from datetime import datetime, timedelta
from fastapi import APIRouter

from app.repositories.oauth_repository import OAuthTokenRepository
from app.repositories.user_repository import UserRepository
from app.service.email_service import EmailService
from uuid import UUID

router = APIRouter(prefix="/emails", tags=["Emails"])

email_service = EmailService()
user_repository = UserRepository()
oauth_repository = OAuthTokenRepository()

@router.post("/adduserdata")
def test_email():
    return email_service.process_message(
        "this is a test email."
    )


@router.post("/seed-test-data")
def seed_test_data():
    try:
        user = user_repository.createUser(name="Test User", email="test@example.com")

        if not user:
            return {"success": False, "message": "Failed to create test user"}

        token = oauth_repository.upsert(
            email=user.email,
            provider="google",
            refresh_token="test-refresh-token",
            access_token="test-access-token",
            expires_at=datetime.utcnow() + timedelta(days=1),
        )

        print(f"Token created: {token}")  # Debugging line

        if not token:
            return {"success": False, "message": "Failed to create test OAuth token"}

        return {
            "success": True,
            "message": "Test data inserted successfully",
            "user_id": str(user.id),
            "email": user.email,
        }
    except Exception as e:
        return {"success": False, "message": str(e)}