from django.core import mail
from django.db import DatabaseError, connection
from django.http import HttpRequest, HttpResponse, JsonResponse


def healthz(request: HttpRequest) -> HttpResponse:  # noqa: ARG001 # request is passed by Django
    db = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            db = result is not None
    except DatabaseError:
        ...

    email = False
    try:
        with mail.get_connection() as email_connection:
            email = email_connection is not None
    except (ConnectionRefusedError, ConnectionAbortedError):
        ...

    if all([db, email]):
        message, code = "ok", 200
    else:
        message, code = "error", 500

    return JsonResponse({"status": message, "db": db, "email": email}, status=code)
