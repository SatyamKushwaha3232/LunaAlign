import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from api.upload import router as upload_router
from api.correspondence import router as correspondence_router


app = FastAPI(
    title="LunaAlgin API",
    description="Multi-Modal Lunar Image Alignment Engine",
    version="1.0.0",
)




# --------------------------------------------------
# CORS
# --------------------------------------------------

default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]
production_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[*default_origins, *production_origins],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/outputs",
    StaticFiles(directory="data/output"),
    name="outputs"
)

app.mount(
    "/input",
    StaticFiles(directory="data/input"),
    name="input"
)

# --------------------------------------------------
# API ROUTERS
# --------------------------------------------------

app.include_router(upload_router)
app.include_router(correspondence_router)

# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "software": "LunaAlgin",
        "message": "LunaAlgin Backend is running",
        "version": "1.0.0",
    }


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "online",
        "software": "LunaAlgin",
        "engine": "Lunar Image Correspondence Engine",
        "version": "1.0.0",
    }
