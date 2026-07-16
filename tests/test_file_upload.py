from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_file_upload_accepts_non_default_form_field_names():
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n"

    with patch(
        "app.router.file_upload.upload_bytes_to_s3",
        return_value={
            "bucket": "test-bucket",
            "key": "uploads/sample.pdf",
            "filename": "sample.pdf",
            "content_type": "application/pdf",
        },
    ) as mock_upload:
        response = client.post(
            "/file-upload/",
            files={"upload": ("sample.pdf", pdf_bytes, "application/pdf")},
        )

    assert response.status_code == 200
    assert response.json()["filename"] == "sample.pdf"
    assert response.json()["content_type"] == "application/pdf"
    assert response.json()["storage"]["bucket"] == "test-bucket"
    mock_upload.assert_called_once()
