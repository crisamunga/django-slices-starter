from datetime import datetime, timedelta
from typing import Any

import pytest
from asgiref.sync import async_to_sync

from ..base import Input, ValidationRule, validate
from ..validators import DateShouldNotBeInFuture

date_not_in_future_scenarios = {
    "date not in future": (datetime.now() - timedelta(days=1), None),
    "date in future": (datetime.now() + timedelta(days=1), ExceptionGroup),
}

sync_validate = async_to_sync(validate)


@pytest.mark.parametrize(
    ("date", "error"), date_not_in_future_scenarios.values(), ids=date_not_in_future_scenarios.keys()
)
def test_date_not_in_future(date: datetime, error: type[Exception] | None) -> None:
    class TestRequest(Input):
        date: datetime

        def as_dict(self) -> dict[str, Any]:
            return {"date": self.date}

        def __init__(self, date: datetime) -> None:
            self.date = date

        @property
        def validators(self) -> dict[str, tuple[ValidationRule, ...]]:
            return {"date": (DateShouldNotBeInFuture(),)}

    request = TestRequest(date=date)

    try:
        sync_validate(
            request,
            base_path=["root"],
        )
    except Exception as e:
        if error is None or not isinstance(e, error):
            raise
