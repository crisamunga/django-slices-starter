from factory.declarations import LazyFunction
from faker import Faker

_faker = Faker()


def factory_fake(provider: str) -> LazyFunction:
    return LazyFunction(lambda *_: getattr(_faker, provider)())  # type: ignore
