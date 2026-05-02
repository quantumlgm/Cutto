from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from .endpoints import router

app = FastAPI()
app.include_router(router)


@app.get("/docs/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        scalar_proxy_url="https://proxy.scalar.com",
    )
