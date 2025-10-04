from typing import Any
from urllib.parse import quote_plus, urlparse


def set_query_params(url: str, params: dict[str, Any] | None = None) -> str:
    parsed_url = urlparse(url)
    query: dict[str, str] = {}
    if params is not None:
        for key, value in params.items():
            if value is None:
                query.pop(key, None)
            else:
                query[key] = ",".join([str(v) for v in value]) if isinstance(value, list) else str(value)
    query_string = "&".join(f"{key}={quote_plus(value)}" for key, value in query.items())
    return parsed_url._replace(query=query_string).geturl()
