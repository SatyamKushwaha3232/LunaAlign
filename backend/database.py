"""MongoDB persistence for LunaAlgin datasets and correspondence jobs."""
import os
from datetime import datetime, timezone
from functools import lru_cache

from pymongo import ASCENDING, DESCENDING, MongoClient


@lru_cache(maxsize=1)
def get_database():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI is not configured. Add it to backend/.env.")
    client = MongoClient(uri, serverSelectionTimeoutMS=8000)
    client.admin.command("ping")
    database = client[os.getenv("MONGODB_DB_NAME", "lunaalgin")]
    database.datasets.create_index("filename", unique=True)
    database.jobs.create_index("job_id", unique=True)
    database.jobs.create_index([("created_at", DESCENDING)])
    return database


def mongo_enabled():
    """Mongo is opt-in so the offline SIH demo works without cloud access."""
    return os.getenv("MONGODB_ENABLED", "false").lower() == "true"


def save_dataset(metadata):
    if not mongo_enabled():
        return
    get_database().datasets.update_one(
        {"filename": metadata["filename"]},
        {"$set": {**metadata, "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )


def list_saved_datasets():
    if not mongo_enabled():
        return None
    records = list(get_database().datasets.find({}, {"_id": 0}).sort("filename", ASCENDING))
    for record in records:
        record.pop("updated_at", None)
    return records


def create_job(job_id, status="queued", stage="queued"):
    if not mongo_enabled():
        return
    get_database().jobs.update_one(
        {"job_id": job_id},
        {"$set": {"status": status, "stage": stage, "created_at": datetime.now(timezone.utc)}},
        upsert=True,
    )


def update_job(job_id, **values):
    if not mongo_enabled():
        return
    values["updated_at"] = datetime.now(timezone.utc)
    get_database().jobs.update_one({"job_id": job_id}, {"$set": values}, upsert=True)


def get_job(job_id, include_result=False):
    if not mongo_enabled():
        return None
    projection = {"_id": 0}
    if not include_result:
        projection["result"] = 0
    return get_database().jobs.find_one({"job_id": job_id}, projection)
