from typing import Any

from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI
from ninja.openapi.docs import DocsBase


def render_stoplight(*, openapi_url: str, title: str) -> HttpResponse:
    html = f"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>{title}</title>
    <!-- Embed elements Elements via Web Component -->
    <script src="https://unpkg.com/@stoplight/elements/web-components.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/@stoplight/elements/styles.min.css">
  </head>
  <body>

    <elements-api
      apiDescriptionUrl="{openapi_url}"
      router="hash"
      layout="responsive"
    />

  </body>
</html>
    """
    return HttpResponse(html)


class StoplightElements(DocsBase):
    def render_page(self, request: HttpRequest, api: NinjaAPI, **kwargs: Any) -> HttpResponse:
        url = self.get_openapi_url(api, kwargs)
        return render_stoplight(
            openapi_url=url,
            title=api.title,
        )
