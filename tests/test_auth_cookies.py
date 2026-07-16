from app.router.auth import build_auth_redirect_response


def test_build_auth_redirect_response_sets_auth_and_user_cookies():
    response = build_auth_redirect_response(
        frontend_url="https://example.com",
        token_payload={"access_token": "abc123", "refresh_token": "refresh123"},
        user_payload={"email": "user@example.com", "name": "User", "id": "123"},
    )

    set_cookie_headers = response.headers.getlist("set-cookie")

    assert any(header.startswith("auth_token=") for header in set_cookie_headers)
    assert any(header.startswith("user=") for header in set_cookie_headers)
