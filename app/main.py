from fastapi import FastAPI
from app.api.routes import meetings

app = FastAPI(title="BBB Microservice")

app.include_router(meetings.router, prefix="/api/meetings", tags=["Meetings"])
