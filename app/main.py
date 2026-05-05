from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from contextlib import asynccontextmanager

from .routers.links import router_link
from .routers.registr import router_auth
from .routers.qr import router_qr
from .config import settings
from .functions import scheduler, link_cleaner

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    scheduler.add_job(
        link_cleaner,
        trigger='interval',
        minutes=5,
        id='link_cleaner_task',
        replace_existing=True
    )
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        scalar_proxy_url="https://proxy.scalar.com",
    )

app.include_router(router_link)
app.include_router(router_qr)
app.include_router(router_auth)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

