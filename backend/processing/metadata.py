from pathlib import Path
import re
import xml.etree.ElementTree as ET


def clean_tag(tag: str) -> str:
    """
    Remove XML namespace and normalize a tag name.
    """
    if not tag:
        return ""

    tag = tag.split("}")[-1]

    return re.sub(
        r"[^a-z0-9]",
        "",
        tag.lower()
    )


def clean_value(value):
    """
    Convert XML text into a clean string.
    """
    if value is None:
        return None

    value = str(value).strip()

    return value if value else None


def xml_values(root):
    """
    Build a normalized XML tag -> value dictionary.
    """
    values = {}

    for element in root.iter():
        tag = clean_tag(element.tag)
        value = clean_value(element.text)

        if tag and value:
            if tag not in values:
                values[tag] = value

    return values


def find_value(values, candidates):
    """
    Find the first matching metadata field.
    """
    for candidate in candidates:
        key = clean_tag(candidate)

        if key in values:
            return values[key]

    return None


def find_float(values, candidates):
    """
    Extract a numeric value from XML metadata.
    """
    value = find_value(values, candidates)

    if value is None:
        return None

    match = re.search(
        r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?",
        value
    )

    if not match:
        return None

    try:
        return float(match.group(0))
    except ValueError:
        return None


def detect_sensor_from_text(text: str):
    """
    Detect Chandrayaan-2 sensor from product metadata.
    """
    if not text:
        return "Unknown"

    value = text.upper()

    if "OHRC" in value or "OHR" in value:
        return "OHRC"

    if "TMC-2" in value or "TMC2" in value:
        return "TMC-2"

    if "TMC" in value:
        return "TMC-2"

    if "IIRS" in value:
        return "IIRS"

    return "Unknown"


def extract_datetime(values):
    """
    Extract acquisition date/time from common
    Chandrayaan/PDS metadata fields.
    """

    # Combined date-time fields
    value = find_value(
        values,
        [
            "start_date_time",
            "startdatetime",
            "start_dateTime",
            "observation_start_time",
            "observationstarttime",
            "acquisition_datetime",
            "acquisitiondatetime",
            "acquisition_date_time",
            "acquisitiondatetime",
            "date_time",
            "datetime",
        ]
    )

    if value:
        return value

    # Separate date + time fields
    date_value = find_value(
        values,
        [
            "start_date",
            "startdate",
            "acquisition_date",
            "acquisitiondate",
            "observation_date",
            "observationdate",
        ]
    )

    time_value = find_value(
        values,
        [
            "start_time",
            "starttime",
            "acquisition_time",
            "acquisitiontime",
            "observation_time",
            "observationtime",
        ]
    )

    if date_value and time_value:
        return f"{date_value}T{time_value}"

    if date_value:
        return date_value

    return None


def extract_resolution(values):
    """
    Extract spatial resolution / pixel scale.
    """
    return find_float(
        values,
        [
            "resolution",
            "spatial_resolution",
            "spatialresolution",
            "pixel_scale",
            "pixelscale",
            "ground_sample_distance",
            "groundsampledistance",
            "grounnd_sample_distance",
            "sampling",
        ]
    )


def extract_sun_azimuth(values):
    """
    Extract solar/sun azimuth angle in degrees.
    """
    return find_float(
        values,
        [
            "sun_azimuth",
            "sunazimuth",
            "solar_azimuth",
            "solarazimuth",
            "illumination_azimuth",
            "illuminationazimuth",
        ]
    )


def extract_sun_elevation(values):
    """
    Extract solar/sun elevation angle in degrees.
    """
    return find_float(
        values,
        [
            "sun_elevation",
            "sunelevation",
            "solar_elevation",
            "solarelevation",
            "illumination_elevation",
            "illuminationelevation",
        ]
    )


def extract_product_type(values):
    """
    Extract product type if present.
    """
    return find_value(
        values,
        [
            "product_type",
            "producttype",
            "processing_level",
            "processinglevel",
            "product_level",
            "productlevel",
        ]
    )


def extract_latitude(values):
    """
    Extract a representative latitude if available.
    """
    return find_float(
        values,
        [
            "latitude",
            "center_latitude",
            "centerlatitude",
            "scene_center_latitude",
            "scenecenterlatitude",
        ]
    )


def extract_longitude(values):
    """
    Extract a representative longitude if available.
    """
    return find_float(
        values,
        [
            "longitude",
            "center_longitude",
            "centerlongitude",
            "scene_center_longitude",
            "scenecenterlongitude",
        ]
    )


def parse_pds_xml(xml_path: str):
    """
    Parse a Chandrayaan/PDS-style XML label.

    The parser intentionally returns None for fields
    that are not available instead of inventing values.
    """

    path = Path(xml_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {path}"
        )

    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except ET.ParseError as error:
        raise ValueError(
            f"Invalid XML metadata: {error}"
        )

    values = xml_values(root)

    # Combine all XML values for sensor detection.
    searchable_text = " ".join(values.values())

    sensor = detect_sensor_from_text(
        searchable_text
    )

    product_id = find_value(
        values,
        [
            "product_id",
            "productid",
            "product_identifier",
            "productidentifier",
            "lidvid",
        ]
    )

    metadata = {
        "product_id": product_id,
        "sensor": sensor,
        "product_type": extract_product_type(values),

        "acquisition": {
            "datetime": extract_datetime(values),
        },

        "spatial": {
            "resolution_m_per_pixel": extract_resolution(values),
        },

        "illumination": {
            "sun_azimuth_deg": extract_sun_azimuth(values),
            "sun_elevation_deg": extract_sun_elevation(values),
        },

        "geolocation": {
            "latitude": extract_latitude(values),
            "longitude": extract_longitude(values),
        },

        "metadata_source": "PDS/XML",
    }

    return metadata