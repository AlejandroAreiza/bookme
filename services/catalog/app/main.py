from fastapi import FastAPI

from app.api import events

app = FastAPI(title="BookMe Catalog")
app.include_router(events.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
