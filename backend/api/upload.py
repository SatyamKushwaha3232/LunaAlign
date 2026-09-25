from pathlib import Path
import re
import shutil
from uuid import uuid4

import cv2
from fastapi import APIRouter, UploadFile, File, HTTPException

from processing.metadata import parse_pds_xml
from database import list_saved_datasets, mongo_enabled, save_dataset

router = APIRouter(
    prefix="/api/v1/datasets",
    tags=["Datasets"]
)

INPUT_DIR = Path("data/input")
INPUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".tif", ".tiff"
}
MAX_UPLOAD_BYTES = 100 * 1024 * 1024


def detect_sensor(filename: str):
    """
    Detect Chandrayaan-2 sensor from filename.

    Supported:
    - OHRC
    - TMC / TMC-2
    - IIRS

    If the filename does not contain a known sensor,
    return Unknown instead of inventing metadata.
    """
    name = filename.upper()

    if "OHRC" in name or "OHR" in name:
        return "OHRC"

    if "TMC" in name:
        return "TMC-2"

    if "IIRS" in name:
        return "IIRS"

    if "LROC" in name or "LRO" in name or "NAC" in name:
        return "LRO/LROC NAC"

    return "Unknown"


def extract_product_id(filename: str):
    """
    Use the filename itself as the product identifier.
    """
    return Path(filename).stem


def extract_acquisition_datetime(filename: str):
    """
    Try to extract Chandrayaan-style timestamp:

    Example:
    ch2_ohr_ncp_20211228T2209123959_d_img_d18

    Returns:
        2021-12-28T22:09:12
    """
    match = re.search(
        r"(20\d{6})T(\d{6})",
        filename
    )

    if not match:
        return None

    date_part = match.group(1)
    time_part = match.group(2)

    try:
        year = date_part[0:4]
        month = date_part[4:6]
        day = date_part[6:8]

        hour = time_part[0:2]
        minute = time_part[2:4]
        second = time_part[4:6]

        return (
            f"{year}-{month}-{day}"
            f"T{hour}:{minute}:{second}"
        )
    except Exception:
        return None


def get_image_metadata(file_path: Path):
    """
    Read basic technical metadata from an image.
    """
    image = cv2.imread(str(file_path))

    if image is None:
        return {
            "dimensions": "Unknown",
            "width": None,
            "height": None,
            "channels": None,
        }

    height, width = image.shape[:2]

    channels = (
        1 if len(image.shape) == 2
        else image.shape[2]
    )

    return {
        "dimensions": f"{width} × {height}",
        "width": width,
        "height": height,
        "channels": channels,
    }


def build_dataset_metadata(file_path: Path):
    """
    Build SIH26166-oriented dataset metadata.

    If a matching PDS/XML sidecar exists, its metadata
    is merged into the image metadata.
    """

    filename = file_path.name

    image_metadata = get_image_metadata(file_path)

    sensor = detect_sensor(filename)

    acquisition_datetime = extract_acquisition_datetime(
        filename
    )

    size_bytes = file_path.stat().st_size

    metadata = {
        "filename": filename,
        "product_id": extract_product_id(filename),

        "sensor": sensor,

        "product_type": "Unknown",

        "acquisition": {
            "datetime": acquisition_datetime,
            "date": (
                acquisition_datetime.split("T")[0]
                if acquisition_datetime
                else None
            ),
        },

        "spatial": {
            "dimensions": image_metadata["dimensions"],
            "width": image_metadata["width"],
            "height": image_metadata["height"],
            "resolution_m_per_pixel": None,
        },

        "illumination": {
            "sun_azimuth_deg": None,
            "sun_elevation_deg": None,
        },

        "geolocation": {
            "latitude": None,
            "longitude": None,
        },

        "file": {
            "extension": file_path.suffix.lower(),
            "format": file_path.suffix.upper().replace(".", ""),
            "size_bytes": size_bytes,
            "size_mb": round(
                size_bytes / (1024 * 1024),
                2
            ),
        },

        "status": "Available",

        "input_url": f"/input/{filename}",

        "metadata_source": "filename + image header",
    }

    # --------------------------------------------------
    # OPTIONAL PDS/XML SIDECAR
    # --------------------------------------------------

    xml_path = file_path.with_suffix(".xml")

    if xml_path.exists():

        try:
            pds_metadata = parse_pds_xml(
                str(xml_path)
            )

            # Product ID
            if pds_metadata.get("product_id"):
                metadata["product_id"] = (
                    pds_metadata["product_id"]
                )

            # Sensor
            if pds_metadata.get("sensor") != "Unknown":
                metadata["sensor"] = (
                    pds_metadata["sensor"]
                )

            # Product type
            if pds_metadata.get("product_type"):
                metadata["product_type"] = (
                    pds_metadata["product_type"]
                )

            # Acquisition
            pds_acquisition = (
                pds_metadata.get("acquisition", {})
            )

            if pds_acquisition.get("datetime"):
                metadata["acquisition"][
                    "datetime"
                ] = pds_acquisition["datetime"]

                metadata["acquisition"]["date"] = (
                    pds_acquisition["datetime"]
                    .split("T")[0]
                )

            # Spatial resolution
            pds_spatial = (
                pds_metadata.get("spatial", {})
            )

            if pds_spatial.get(
                "resolution_m_per_pixel"
            ) is not None:
                metadata["spatial"][
                    "resolution_m_per_pixel"
                ] = pds_spatial[
                    "resolution_m_per_pixel"
                ]

            # Illumination
            pds_illumination = (
                pds_metadata.get(
                    "illumination",
                    {}
                )
            )

            if pds_illumination.get(
                "sun_azimuth_deg"
            ) is not None:
                metadata["illumination"][
                    "sun_azimuth_deg"
                ] = pds_illumination[
                    "sun_azimuth_deg"
                ]

            if pds_illumination.get(
                "sun_elevation_deg"
            ) is not None:
                metadata["illumination"][
                    "sun_elevation_deg"
                ] = pds_illumination[
                    "sun_elevation_deg"
                ]

            # Geolocation
            pds_geolocation = (
                pds_metadata.get(
                    "geolocation",
                    {}
                )
            )

            if pds_geolocation.get(
                "latitude"
            ) is not None:
                metadata["geolocation"][
                    "latitude"
                ] = pds_geolocation[
                    "latitude"
                ]

            if pds_geolocation.get(
                "longitude"
            ) is not None:
                metadata["geolocation"][
                    "longitude"
                ] = pds_geolocation[
                    "longitude"
                ]

            metadata["metadata_source"] = (
                "PDS/XML + image header"
            )

        except Exception as error:

            metadata["metadata_source"] = (
                "filename + image header"
            )

            metadata["metadata_warning"] = (
                f"PDS/XML parsing failed: {error}"
            )

    return metadata

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...)
):
    """
    Upload a lunar image into the processing dataset.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is missing."
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported image format. "
                "Use JPG, JPEG, PNG, TIF or TIFF."
            )
        )

    safe_name = Path(file.filename).name

    # Avoid overwriting an earlier dataset with the same browser filename.
    output_path = INPUT_DIR / safe_name
    if output_path.exists():
        output_path = INPUT_DIR / f"{output_path.stem}_{uuid4().hex[:8]}{output_path.suffix}"

    try:
        with output_path.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
                length=1024 * 1024,
            )
            if buffer.tell() > MAX_UPLOAD_BYTES:
                buffer.close()
                output_path.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="Image exceeds the 100 MB upload limit.")
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to save uploaded image: {error}"
        )

    if cv2.imread(str(output_path), cv2.IMREAD_UNCHANGED) is None:
        output_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="The uploaded file is corrupted or is not a supported image.")

    metadata = build_dataset_metadata(
        output_path
    )
    # Atlas is for persistence, not a prerequisite for image processing. A
    # transient Atlas/DNS/network outage must not reject a valid upload.
    database_status = "disabled"
    database_warning = None
    if mongo_enabled():
        if save_dataset(metadata):
            database_status = "saved"
        else:
            database_status = "unavailable"
            database_warning = (
                "MongoDB metadata sync is temporarily unavailable. "
                "This image was saved locally and can still be used for correspondence."
            )
            metadata["database_warning"] = database_warning

    return {
        "status": "uploaded",
        "filename": output_path.name,
        "path": str(output_path),
        "metadata": metadata,
        "database_status": database_status,
        "database_warning": database_warning,
        "message": "Lunar image uploaded successfully.",
    }


@router.get("")
def list_datasets():
    """
    Return all uploaded lunar images
    with SIH26166-oriented metadata.
    """

    if mongo_enabled():
        try:
            datasets = list_saved_datasets()
            return {"status": "success", "count": len(datasets), "datasets": datasets}
        except Exception:
            # Keep the Datasets page available when Atlas is temporarily down.
            pass

    datasets = []

    for file_path in sorted(INPUT_DIR.iterdir()):

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        try:
            metadata = build_dataset_metadata(
                file_path
            )

            datasets.append(metadata)

        except Exception as error:
            datasets.append({
                "filename": file_path.name,
                "product_id": file_path.stem,
                "sensor": "Unknown",
                "product_type": "Unknown",
                "acquisition": {
                    "datetime": None,
                    "date": None,
                },
                "spatial": {
                    "dimensions": "Unknown",
                    "width": None,
                    "height": None,
                    "resolution_m_per_pixel": None,
                },
                "illumination": {
                    "sun_azimuth_deg": None,
                    "sun_elevation_deg": None,
                },
                "geolocation": {
                    "latitude": None,
                    "longitude": None,
                },
                "file": {
                    "extension": file_path.suffix.lower(),
                    "format": file_path.suffix.upper().replace(".", ""),
                    "size_bytes": file_path.stat().st_size,
                    "size_mb": round(
                        file_path.stat().st_size
                        / (1024 * 1024),
                        2
                    ),
                },
                "status": "Metadata Error",
                "input_url": f"/input/{file_path.name}",
                "metadata_source": str(error),
            })

    return {
        "status": "success",
        "count": len(datasets),
        "datasets": datasets,
    }
