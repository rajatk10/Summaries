import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.responses import HTMLResponse
from tortoise.contrib.fastapi import RegisterTortoise

from app.api.ping import router as ping_router
from app.api.summaries import router as summary_router
from app.config import TORTOISE_ORM, configure_logging, settings

configure_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info(
        f"Starting Summary API Application, environment = {settings.environment}"
    )
    try:
        async with RegisterTortoise(app=app, config=TORTOISE_ORM):
            yield
    except Exception as e:
        logger.error(f"Summary API Application Error = {e}")
        raise
    finally:
        logger.info("Stopping Summary API Application")


app = FastAPI(title="Summaries FastAPI", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def index():
    logger.info("root api endpoint '/' ")
    return "<h1>Hello, Welcome to Summaries API!</h1>"


app.include_router(ping_router)
app.include_router(summary_router)
