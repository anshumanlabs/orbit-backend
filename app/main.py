from fastapi import FastAPI
from app.router.email import router as email_router
from app.router.auth import router as auth_router
from app.router.file_upload import router as file_upload_router

app = FastAPI(
    title="Orbit AI Assistant",
    version="1.0.0"
)

app.include_router(email_router)
app.include_router(auth_router)
app.include_router(file_upload_router)