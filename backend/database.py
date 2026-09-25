"""Optional MongoDB persistence for LunaAlgin datasets and correspondence jobs."""
import os
from datetime import datetime, timezone
from functools import lru_cache
from time import monotonic

from pymongo import ASCENDING, DESCENDING, MongoClient

# If Atlas/DNS is unavailable, avoid retrying every upload/job-stage request.
# Files and in-memory jobs remain fully usable while this short circuit is active.
_RETRY_AFTER = 0.0
_RETRY_DELAY_SECONDS = 60.0


def mongo_enabled():
    """Mongo is optional; LunaAlgin's processing pipeline works without it."""
    return os.getenv("MONGODB_ENABLED", "false").lower() == "true"


def _can_attempt_connection():
    return monotonic() >= _RETRY_AFTER


def _mark_unavailable():
    global _RETRY_AFTER
    _RETRY_AFTER = monotonic() + _RETRY_DELAY_SECONDS
    get_database.cache_clear()


@lru_cache(maxsize=1)
def get_database():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI is not configured. Add it to backend/.env.")
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=2500,
        connectTimeoutMS=2500,
        socketTimeoutMS=2500,
    )
    client.admin.command("ping")
    database = client[os.getenv("MONGODB_DB_NAME", "lunaalgin")]
    database.datasets.create_index("filename", unique=True)
    database.jobs.create_index("job_id", unique=True)
    database.jobs.create_index([("created_at", DESCENDING)])
    return database


def save_dataset(metadata):
    """Persist metadata when available; return False instead of breaking upload."""
    if not mongo_enabled() or not _can_attempt_connection():
        return False
    try:
        get_database().datasets.update_one(
            {"filename": metadata["filename"]},
            {"$set": {**metadata, "updated_at": datetime.now(timezone.utc)}},
            upsert=True,
        )
        return True
    except Exception:
        _mark_unavailable()
        return False


def list_saved_datasets():
    if not mongo_enabled() or not _can_attempt_connection():
        return None
    try:
        records = list(get_database().datasets.find({}, {"_id": 0}).sort("filename", ASCENDING))
        for record in records:
            record.pop("updated_at", None)
        return records
    except Exception:
        _mark_unavailable()
        return None


def create_job(job_id, status="queued", stage="queued"):
    if not mongo_enabled() or not _can_attempt_connection():
        return False
    try:
        get_database().jobs.update_one(
            {"job_id": job_id},
            {"$set": {"status": status, "stage": stage, "created_at": datetime.now(timezone.utc)}},
            upsert=True,
        )
        return True
    except Exception:
        _mark_unavailable()
        return False


def update_job(job_id, **values):
    if not mongo_enabled() or not _can_attempt_connection():
        return False
    try:
        values["updated_at"] = datetime.now(timezone.utc)
        get_database().jobs.update_one({"job_id": job_id}, {"$set": values}, upsert=True)
        return True
    except Exception:
        _mark_unavailable()
        return False


def get_job(job_id, include_result=False):
    if not mongo_enabled() or not _can_attempt_connection():
        return None
    try:
        projection = {"_id": 0}
        if not include_result:
            projection["result"] = 0
        return get_database().jobs.find_one({"job_id": job_id}, projection)
    except Exception:
        _mark_unavailable()
        return None