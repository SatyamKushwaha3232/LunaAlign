from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
)


def _value(value, fallback="-"):
    return fallback if value is None or value == "" else str(value)


def _metric_rows(result):
    geometry = result.get("geometry", {})
    metrics = result.get("registration", {}).get("quality_metrics", {})
    error = geometry.get("reprojection_error", {})
    return [
        ["Feature matches", _value(result.get("matching", {}).get("good_matches"))],
        ["RANSAC inliers", _value(geometry.get("inliers"))],
        ["Inlier ratio", f"{_value(geometry.get('inlier_ratio'))}%"],
        ["Mean reprojection error", f"{_value(error.get('mean_error'))} px"],
        ["RMSE", _value(metrics.get("rmse"))],
        ["SSIM", _value(metrics.get("ssim"))],
        ["NCC", _value(metrics.get("ncc"))],
        ["Processing time", f"{_value(result.get('processing_time_seconds'))} s"],
    ]


def create_scientific_report(result: dict, job_dir: Path) -> Path:
    """Generate a compact, job-specific LunaAlgin PDF report."""
    output_path = job_dir / "lunaalgin_report.pdf"
    document = SimpleDocTemplate(
        str(output_path), pagesize=A4, rightMargin=1.5 * cm,
        leftMargin=1.5 * cm, topMargin=1.4 * cm, bottomMargin=1.4 * cm,
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleLuna", parent=styles["Title"], textColor=colors.HexColor("#123968")))
    styles.add(ParagraphStyle(name="SmallLuna", parent=styles["BodyText"], fontSize=8, leading=11, textColor=colors.HexColor("#425466")))
    story = [
        Paragraph("LUNAALGIN", styles["TitleLuna"]),
        Paragraph("Lunar Image Correspondence Report", styles["Heading2"]),
        Paragraph(f"Job ID: {_value(result.get('job_id'))}", styles["SmallLuna"]), Spacer(1, 12),
    ]
    metadata = result.get("metadata", {})
    reference = metadata.get("reference", {})
    target = metadata.get("target", {})
    info = [
        ["", "Reference", "Target"],
        ["Product", _value(reference.get("product_id"), result.get("input", {}).get("reference")), _value(target.get("product_id"), result.get("input", {}).get("target"))],
        ["Sensor", _value(reference.get("sensor")), _value(target.get("sensor"))],
        ["Acquisition", _value(reference.get("acquisition", {}).get("datetime")), _value(target.get("acquisition", {}).get("datetime"))],
        ["Sun azimuth", _value(reference.get("illumination", {}).get("sun_azimuth_deg")), _value(target.get("illumination", {}).get("sun_azimuth_deg"))],
        ["Sun elevation", _value(reference.get("illumination", {}).get("sun_elevation_deg")), _value(target.get("illumination", {}).get("sun_elevation_deg"))],
    ]
    story += [Paragraph("Input and illumination", styles["Heading3"]), _table(info, [3.2 * cm, 6.1 * cm, 6.1 * cm]), Spacer(1, 12)]
    story += [Paragraph("Registration metrics", styles["Heading3"]), _table(_metric_rows(result), [8 * cm, 7.4 * cm]), Spacer(1, 12)]
    transform = result.get("transformation", {})
    matrix = transform.get("matrix", [])
    story += [Paragraph(f"Transformation - {_value(transform.get('model'))}", styles["Heading3"])]
    story += [_table([[" ".join(f"{float(value):.6f}" for value in row)] for row in matrix] or [["Unavailable"]], [15.4 * cm]), Spacer(1, 12)]
    confidence = result.get("confidence", {})
    story += [Paragraph(f"{_value(confidence.get('label'))}: <b>{_value(confidence.get('score'))}%</b>", styles["BodyText"]), Spacer(1, 14)]
    image_paths = [("Aligned image", job_dir / "aligned.png"), ("Correspondence map", job_dir / "matches.png"), ("Difference map", job_dir / "difference.png")]
    for title, path in image_paths:
        if path.exists():
            story += [KeepTogether([
                Paragraph(title, styles["Heading3"]),
                Image(str(path), width=15.4 * cm, height=8.5 * cm, kind="proportional"),
                Spacer(1, 10),
            ])]
    if result.get("validation"):
        validation = result["validation"]
        story += [PageBreak(), Paragraph("Ground-truth validation", styles["Heading3"]), _table([
            ["Test type", _value(validation.get("type"))],
            ["Corner RMSE", f"{_value(validation.get('corner_rmse_px'))} px"],
            ["Conditions", _value(validation.get("test_conditions"))],
        ], [4 * cm, 11.4 * cm])]
    document.build(story)
    return output_path


def _table(rows, widths):
    table = Table(rows, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9F3FC")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#172B4D")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B6CADB")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table
