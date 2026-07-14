from fastapi import APIRouter
from app.service.email_service import EmailService

router = APIRouter(prefix="/emails", tags=["Emails"])

email_service = EmailService()

@router.get("/")
def test_email():
    return email_service.process_message(
        "this is a test email."
    )