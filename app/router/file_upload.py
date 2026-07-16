from fastapi import APIRouter, File, HTTPException, UploadFile

from app.service.file_storage_service import upload_bytes_to_s3

router = APIRouter(
    prefix="/file-upload",
    tags=["File Upload"]
)


@router.post("/")
async def upload_file(
    file: UploadFile | None = File(default=None),
    upload: UploadFile | None = File(default=None),
):
    selected_file = upload or file

    if selected_file is None:
        raise HTTPException(status_code=400, detail="No file uploaded")

    contents = await selected_file.read()

    try:
        storage_result = upload_bytes_to_s3(
            contents,
            filename=selected_file.filename or "upload.bin",
            content_type=selected_file.content_type,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(exc)}") from exc

    print(f"Received file: {selected_file.filename}, content type: {selected_file.content_type}")
    return {
        "filename": selected_file.filename,
        "content_type": selected_file.content_type,
        "storage": storage_result,
    }