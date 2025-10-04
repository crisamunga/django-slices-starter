import json
from functools import partial
from typing import Any

from django.http import HttpRequest
from ninja.responses import NinjaJSONEncoder


class JsonEncoder(NinjaJSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, HttpRequest):
            return {
                "method": obj.method,
                "path": obj.path,
                "GET": dict(obj.GET),
                "user": str(obj.user),
            }

        # Let the base class default method raise the TypeError
        return super().default(obj)


dumps = partial(json.dumps, cls=JsonEncoder)
loads = json.loads
