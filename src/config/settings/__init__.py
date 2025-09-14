import os

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    from .prod import *
else:
    from .dev import *
