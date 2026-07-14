from uuid import UUID
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models.messages import Message

class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: UUID,
        gmail_message_id: Optional[str] = None,
        account_email: Optional[str] = None,
        subject: Optional[str] = None,
        sender: Optional[str] = None,
        body: Optional[str] = None,
        received_at: Optional[datetime] = None,
    ) -> Message:
        message = Message(
            user_id=user_id,
            gmail_message_id=gmail_message_id,
            account_email=account_email,
            subject=subject,
            sender=sender,
            body=body,
            received_at=received_at,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_by_id(self, message_id: UUID) -> Optional[Message]:
        return self.db.query(Message).filter(Message.id == message_id).first()

    def get_by_user_id(self, user_id: UUID) -> list[Message]:
        return self.db.query(Message).filter(Message.user_id == user_id).all()

    def get_by_gmail_message_id(self, gmail_message_id: str) -> Optional[Message]:
        return self.db.query(Message).filter(Message.gmail_message_id == gmail_message_id).first()
