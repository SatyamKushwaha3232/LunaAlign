from pathlib import Path
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException


router = APIRouter(
    prefix="/api/v1/datasets",
    tags=["Datasets"]
)

INPUT_DIR = Path("data/input")
INPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".tif",
    ".tiff"
}


@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...)
):
    """
    Upload a lunar image for LunaAlgin processing.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is missing."
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported image format. "
                "Use JPG, JPEG, PNG, TIF or TIFF."
            )
        )

    safe_name = Path(
        file.filename
    ).name

    output_path = INPUT_DIR / safe_name

    with output_path.open("wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    return {
        "status": "uploaded",
        "filename": safe_name,
        "path": str(output_path),
        "message": "Lunar image uploaded successfully."
    }