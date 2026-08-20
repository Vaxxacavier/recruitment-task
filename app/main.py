from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import books


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Library Management API",
    description=(
        "REST API for managing a library's book catalogue.\n\n"
        "Supports adding/removing books and tracking borrow status."
    ),
    version="1.0.0",
    lifespan=lifespan,
    redoc_url=None,
)

app.include_router(books.router)


@app.get("/health", tags=["system"], summary="Health check")
def health() -> dict:
    return {"status": "ok"}
