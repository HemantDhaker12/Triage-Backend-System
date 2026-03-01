from fastapi import FastAPI
from sqlmodel import SQLModel
from app.core.database import engine
from app.api.incidents import router

app = FastAPI(title="Incident Triage System")


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


app.include_router(router)


@app.get("/")
def health():
    return {"status": "ok"}