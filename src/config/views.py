from django.db import DatabaseError, connection
from django.http import HttpRequest, HttpResponse, JsonResponse


def healthz(request: HttpRequest) -> HttpResponse:  # noqa: ARG001 # request is passed by Django
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
    except DatabaseError:
        return JsonResponse({"status": "error", "message": "Unable to connect to the database"}, status=500)

    return JsonResponse({"status": "ok", "db_connection": result is not None})
