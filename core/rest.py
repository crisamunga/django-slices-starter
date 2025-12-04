from ninja import Router

from .auth import rest as auth

router = Router()

router.add_router("", auth.router)
