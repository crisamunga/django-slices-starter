import re
from typing import Any

import httpx
import pytest
from allauth.account.models import EmailAddress
from django.core import mail
from faker import Faker
from pytest_django.live_server_helper import LiveServer

from ..models import User
from .factories import UserFactory, generate_totp

# This test suite covers the ideal path for authentication flows. It does not fully cover all edge cases.


@pytest.fixture
def auth_client(live_server: LiveServer) -> httpx.Client:
    return httpx.Client(
        base_url=f"{live_server.url}/_accounts/app/v1",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )


@pytest.fixture
def verified_user() -> User:
    user = UserFactory.create()
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=True,
        primary=True,
    )
    return user


@pytest.mark.django_db
def test_app_sign_up_flow_ok(faker: Faker, auth_client: httpx.Client) -> None:
    email = faker.email()
    password = faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)

    # Sign up

    body = {
        "email": email,
        "password": password,
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
    }
    response = auth_client.post("auth/signup", json=body)
    assert response.status_code == 401, "Sign up should result in unauthenticated session"
    data = response.json()
    session_token = data["meta"]["session_token"]
    assert data["meta"]["is_authenticated"] is False
    assert session_token
    assert ("verify_email", True) in {(f["id"], f.get("is_pending")) for f in data["data"]["flows"]}

    auth_client.headers.update({"X-Session-Token": session_token})

    # Check email
    assert len(mail.outbox) >= 1
    assert mail.outbox[-1].to == [email]

    match = re.search(r"Please enter it in your open browser window.\n\n(\w+)\n\n", str(mail.outbox[-1].body))
    assert match
    assert len(match.groups()) == 1
    code = match.group(1)

    # Verify email
    body = {"key": code}
    response = auth_client.post("auth/email/verify", json=body)

    assert response.status_code == 200, "Email verification should succeed"
    data = response.json()
    assert data["meta"]["is_authenticated"] is True
    assert data["data"]["user"]["email"] == email

    # Log in
    auth_client.headers.pop("X-Session-Token")
    body = {"email": email, "password": password}
    response = auth_client.post("auth/login", json=body)
    assert response.status_code == 200, "Login should succeed"
    data = response.json()
    assert data["meta"]["is_authenticated"] is True
    assert data["data"]["user"]["email"] == email
    session_token = data["meta"]["session_token"]
    assert session_token


@pytest.mark.django_db
def test_password_reset_flow_ok(verified_user: User, faker: Faker, auth_client: httpx.Client) -> None:
    old_password = faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
    verified_user.set_password(old_password)

    new_password = faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)

    # Request password reset
    body = {"email": verified_user.email}
    response = auth_client.post("auth/password/request", json=body)
    assert response.status_code == 401, "Password reset request should succeed"
    data = response.json()
    session_token = data["meta"]["session_token"]
    assert data["meta"]["is_authenticated"] is False
    assert session_token
    assert ("password_reset_by_code", True) in {(f["id"], f.get("is_pending")) for f in data["data"]["flows"]}

    auth_client.headers.update({"X-Session-Token": session_token})

    # Check email
    assert len(mail.outbox) >= 1
    assert mail.outbox[-1].to == [verified_user.email]

    match = re.search(r"Please enter it in your open browser window.\n\n(\w+)\n\n", str(mail.outbox[-1].body))
    assert match
    assert len(match.groups()) == 1
    code = match.group(1)

    # Reset password
    body = {"key": code, "password": new_password}
    response = auth_client.post("auth/password/reset", json=body)
    assert response.status_code == 401, "Password reset should succeed"
    data = response.json()
    assert data["meta"]["is_authenticated"] is False
    assert ("password_reset_by_code", False) in {(f["id"], f.get("is_pending")) for f in data["data"]["flows"]}

    # Log in with new password
    auth_client.headers.pop("X-Session-Token")
    body = {"email": verified_user.email, "password": new_password}
    response = auth_client.post("auth/login", json=body)
    assert response.status_code == 200, "Login with new password should succeed"
    data = response.json()
    assert data["meta"]["is_authenticated"] is True
    assert data["data"]["user"]["email"] == verified_user.email


@pytest.mark.django_db
def test_app_mfa_flow_ok(settings: Any, auth_client: httpx.Client, verified_user: User, faker: Faker) -> None:  # noqa: PLR0915
    password = faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
    verified_user.set_password(password)
    verified_user.save()
    settings.DEBUG = True

    # Log in
    body = {"email": verified_user.email, "password": password}
    response = auth_client.post("auth/login", json=body)
    assert response.status_code == 200, "Login should succeed"
    data = response.json()
    assert data["meta"]["is_authenticated"] is True
    assert data["data"]["user"]["email"] == verified_user.email
    session_token = data["meta"]["session_token"]
    assert session_token
    auth_client.headers.update({"X-Session-Token": session_token})

    # Fetch TOTP details
    response = auth_client.get("/account/authenticators/totp")
    assert response.status_code == 404, "TOTP details should not exist yet"
    data = response.json()
    secret = data["meta"]["secret"]
    assert secret

    # Re-authenticate
    body = {"password": password}
    response = auth_client.post("auth/reauthenticate", json=body)
    assert response.status_code == 200, "Re-authentication should succeed"

    # Enable TOTP
    totp_code = generate_totp(secret=secret)
    body = {"code": totp_code}
    response = auth_client.post("/account/authenticators/totp", json=body)
    assert response.status_code == 200, "Enabling TOTP should succeed"

    # Get recovery codes
    response = auth_client.get("/account/authenticators/recovery-codes")
    assert response.status_code == 200, "Generating recovery codes should succeed"
    data = response.json()
    recovery_codes = data["data"]["unused_codes"]
    assert len(recovery_codes) == 10

    # Log out
    response = auth_client.delete("auth/session")
    assert response.status_code == 401, "Logout should succeed"
    auth_client.headers.pop("X-Session-Token")

    # Log in with TOTP
    body = {"email": verified_user.email, "password": password}
    response = auth_client.post("auth/login", json=body)
    assert response.status_code == 401, "Login requiring TOTP should return unauthenticated session"
    data = response.json()
    session_token = data["meta"]["session_token"]
    assert data["meta"]["is_authenticated"] is False
    assert ("mfa_authenticate", True) in {(f["id"], f.get("is_pending")) for f in data["data"]["flows"]}
    auth_client.headers.update({"X-Session-Token": session_token})

    # Provide TOTP code
    totp_code = generate_totp(secret=secret)
    body = {"code": totp_code}
    response = auth_client.post("auth/2fa/authenticate", json=body)
    assert response.status_code == 200, "TOTP authentication should succeed"
    data = response.json()
    assert data["meta"]["is_authenticated"] is True
    assert data["data"]["user"]["email"] == verified_user.email

    # Log out
    auth_client.headers.pop("X-Session-Token")

    # Log in with Recovery code
    body = {"email": verified_user.email, "password": password}
    response = auth_client.post("auth/login", json=body)
    assert response.status_code == 401, "Login requiring TOTP should return unauthenticated session"
    data = response.json()
    session_token = data["meta"]["session_token"]
    assert data["meta"]["is_authenticated"] is False
    assert ("mfa_authenticate", True) in {(f["id"], f.get("is_pending")) for f in data["data"]["flows"]}
    auth_client.headers.update({"X-Session-Token": session_token})

    # Provide Recovery code
    body = {"code": recovery_codes[0]}
    response = auth_client.post("auth/2fa/authenticate", json=body)
    assert response.status_code == 200, "TOTP authentication should succeed"
    data = response.json()
    assert data["meta"]["is_authenticated"] is True
    assert data["data"]["user"]["email"] == verified_user.email
