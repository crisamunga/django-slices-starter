from django.conf import settings

from core.rest import router as core
from lib.rest import create_api

api = create_api(
    app_name=settings.APP_NAME,
    urls_namespace="api",
)


api.add_router("", core)
