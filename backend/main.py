import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import analyze, chat

app = FastAPI(title="Kubu-Hai AI Backend")

# Set KUBUVERSE_CORS_ORIGINS to a comma-separated list of trusted frontend
# origins in each deployment environment. Local development remains usable.
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "KUBUVERSE_CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(analyze.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Kubu-Hai Backend is running"}
