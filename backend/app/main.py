from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.core.database import check_database_connection
from app.core.errors import install_error_handlers
from app.modules.auth.router import router as auth_router

app = FastAPI(title="Medical Records API", version="0.1.0")
install_error_handlers(app)
app.include_router(auth_router)


class HealthResponse(BaseModel):
    status: str


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    if not check_database_connection():
        raise HTTPException(
            status_code=503,
            detail="Database connection unavailable",
        )
    return HealthResponse(status="ok")
