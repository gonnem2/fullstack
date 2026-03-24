import asyncio
from contextlib import asynccontextmanager
from inspect import iscoroutine, iscoroutinefunction

from fastapi import FastAPI

from app.service.user.callbacks import startup_callbacks as user_startup_callbacks


startup_callbacks = list()
startup_callbacks.extend(user_startup_callbacks)


@asynccontextmanager
async def lifespan(app: FastAPI):

    for startup_callback in startup_callbacks:
        if not iscoroutinefunction(startup_callback):
            startup_callback()
        else:
            asyncio.create_task(startup_callback())

    yield
