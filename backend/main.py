from fastapi import FastAPI
from . import models
from .database import engine
from .routers import proposals

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DAO Governance Swarms API",
    description="A backend system for a multi-agent DAO governance platform based on the ASI Alliance stack.",
    version="1.0.0",
)

# Include the API router
app.include_router(proposals.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the DAO Governance Swarms API"}