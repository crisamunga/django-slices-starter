# ------------------------------------------------------------------------------------------------
# CUSTOM PROJECT SETTINGS
#
# Environment variables used:
#   API_PAGINATION_MAX_LIMIT  - Maximum number of items per page for paginated endpoints (default: 100)
# ------------------------------------------------------------------------------------------------

import os

from .deployment import APP_DOMAIN

API_PAGINATION_MAX_LIMIT = int(os.getenv("API_PAGINATION_MAX_LIMIT", "100"))

__all__ = [
    "API_PAGINATION_MAX_LIMIT",
]
