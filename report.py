# Reporting Module (Function 7)
#
# Hides the report layouts and the export file formats. Reads the stored
# records only through event_log.searchLog and never changes them.
#
# Interface:
#   generateReport(reportType, fromDate, toDate) -> report (dict)
#       reportType in {"Usage", "Downtime", "Alarm"}; dates are date or datetime,
#       toDate is inclusive. Raises ValueError for a bad type or fromDate > toDate.
#       A range with no records gives an empty report (no error).
#   exportReport(report, format, path=None) -> path of the written file
#       format in {"CSV", "PDF"}. Raises ValueError for a bad format and
#       Exception if the file cannot be written.
#   formatReport(report) -> str (plain-text version, for printing on screen)
#
# report = {"type", "from", "to", "generated", "title", "summary": [(label, value)],
#           "columns": [...], "rows": [[...]], "empty": bool}

from datetime import datetime, date, time

from event_log import searchLog

REPORT_TYPES = ["Usage", "Downtime", "Alarm"]
EXPORT_FORMATS = ["CSV", "PDF"]


def _day(value):

    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return value.strftime("%Y-%m-%d")


def _as_start(value):

    return value if isinstance(value, datetime) else datetime.combine(value, time.min)


def _as_end(value):

    return value if isinstance(value, datetime) else datetime.combine(value, time.max)


def _seconds_text(seconds):

    seconds = int(round(seconds))
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}h {minutes:02d}m {secs:02d}s"


# ---------------------------------------------------------------- report types

def _usage_report(records):

    per_cabinet = {}

    for r in records:
        counts = per_cabinet.setdefault(r["cabinet"], {})
        counts[r["type"]] = counts.get(r["type"], 0) + 1

    types = ["Status", "Inventory", "Alarm", "Maintenance", "Health"]
    rows = []
    for cabinet in sorted(per_cabinet):
        counts = per_cabinet[cabinet]
        rows.append([cabinet] + [counts.get(t, 0) for t in types] + [sum(counts.values())])

    low_stock = sum(
        1 for r in records
        if r["type"] == "Inventory" and r["details"].get("low")
    )
    faults = sum(
        1 for r in records
        if r["type"] == "Health" and r["details"].get("state") == "Fault"
    )

    summary = [
        ("Total events", len(records)),
        ("Cabinets reporting", len(per_cabinet)),
        ("Low-stock events", low_stock),
        ("Fault events", faults),
    ]

    return summary, ["Cabinet"] + types + ["Total"], rows


def _downtime_report(records, start, end):

    # Walk each cabinet's Status events in time order. An "Offline" status opens
    # a downtime interval, the next "Online" closes it. An interval still open at
    # the end of the range is closed at the end of the range (or "now" if earlier).
    stop = min(end, datetime.now()) if end > datetime.now() else end

    per_cabinet = {}
    for r in records:
        if r["type"] == "Status":
            per_cabinet.setdefault(r["cabinet"], []).append(r)

    rows = []
    total_seconds = 0
    total_outages = 0

    for cabinet in sorted(per_cabinet):
        down_since = None
        for r in per_cabinet[cabinet]:
            status = r["details"].get("status")
            if status == "Offline" and down_since is None:
                down_since = r["timestamp"]
            elif status == "Online" and down_since is not None:
                seconds = (r["timestamp"] - down_since).total_seconds()
                rows.append([cabinet,
                             down_since.strftime("%Y-%m-%d %H:%M:%S"),
                             r["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                             _seconds_text(seconds)])
                total_seconds += seconds
                total_outages += 1
                down_since = None
        if down_since is not None:
            seconds = max((stop - down_since).total_seconds(), 0)
            rows.append([cabinet,
                         down_since.strftime("%Y-%m-%d %H:%M:%S"),
                         "still offline",
                         _seconds_text(seconds)])
            total_seconds += seconds
            total_outages += 1

    summary = [
        ("Outages", total_outages),
        ("Cabinets affected", len({row[0] for row in rows})),
        ("Total downtime", _seconds_text(total_seconds)),
    ]

    return summary, ["Cabinet", "Went offline", "Back online", "Duration"], rows


def _alarm_report(records):

    alarms = [r for r in records if r["type"] == "Alarm"]

    by_severity = {}
    by_cabinet = {}
    for r in alarms:
        severity = r["details"].get("severity", "Unknown")
        by_severity[severity] = by_severity.get(severity, 0) + 1
        by_cabinet[r["cabinet"]] = by_cabinet.get(r["cabinet"], 0) + 1

    rows = [
        [r["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
         r["cabinet"],
         r["details"].get("severity", "Unknown"),
         r["details"].get("reason", "")]
        for r in alarms
    ]

    summary = [("Total alarms", len(alarms))]
    for severity in sorted(by_severity):
        summary.append((f"{severity} alarms", by_severity[severity]))
    for cabinet in sorted(by_cabinet):
        summary.append((f"Alarms from {cabinet}", by_cabinet[cabinet]))

    return summary, ["Time", "Cabinet", "Severity", "Reason"], rows


# ------------------------------------------------------------------ public API

def generateReport(reportType, fromDate, toDate):

    if reportType not in REPORT_TYPES:
        raise ValueError(f"Invalid report type: {reportType}")
    if _as_start(fromDate) > _as_end(toDate):
        raise ValueError("fromDate must not be after toDate")

    records = searchLog(fromDate=fromDate, toDate=toDate)

    if reportType == "Usage":
        summary, columns, rows = _usage_report(records)
    elif reportType == "Downtime":
        summary, columns, rows = _downtime_report(records, _as_start(fromDate), _as_end(toDate))
    else:
        summary, columns, rows = _alarm_report(records)

    return {
        "type": reportType,
        "from": fromDate,
        "to": toDate,
        "generated": datetime.now(),
        "title": f"{reportType} Report  ({_day(fromDate)} to {_day(toDate)})",
        "summary": summary,
        "columns": columns,
        "rows": rows,
        "empty": len(rows) == 0,
    }


def formatReport(report):

    lines = ["", "===================================", f"  {report['title']}",
             "==================================="]

    if report["empty"]:
        lines.append("No records in this date range.")
        return "\n".join(lines)

    lines.append("\nSUMMARY")
    lines.append("-----------------------------------")
    for label, value in report["summary"]:
        lines.append(f"{label}: {value}")

    lines.append("\nDETAILS")
    lines.append("-----------------------------------")
    lines.append(" | ".join(report["columns"]))
    for row in report["rows"]:
        lines.append(" | ".join(str(cell) for cell in row))

    return "\n".join(lines)


def exportReport(report, format, path=None):

    format = str(format).upper()
    if format not in EXPORT_FORMATS:
        raise ValueError(f"Invalid export format: {format}")

    if path is None:
        stamp = report["generated"].strftime("%Y%m%d_%H%M%S")
        path = f"{report['type'].lower()}_report_{stamp}.{format.lower()}"

    try:
        if format == "CSV":
            _write_csv(report, path)
        else:
            _write_pdf(report, path)
    except Exception as error:
        raise Exception(f"Report could not be written: {error}")

    return path


# --------------------------------------------------------------- file writers

def _write_csv(report, path):

    import csv

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([report["title"]])
        writer.writerow(["Generated", report["generated"].strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow([])
        for label, value in report["summary"]:
            writer.writerow([label, value])
        writer.writerow([])
        if report["empty"]:
            writer.writerow(["No records in this date range."])
        else:
            writer.writerow(report["columns"])
            writer.writerows(report["rows"])


def _write_pdf(report, path):

    # reportlab is only needed for PDF export, so it is imported here.
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path, pagesize=landscape(letter))
    story = [
        Paragraph("Hospital ADC Monitoring System", styles["Title"]),
        Paragraph(report["title"], styles["Heading2"]),
        Paragraph("Generated " + report["generated"].strftime("%Y-%m-%d %H:%M:%S"), styles["Normal"]),
        Spacer(1, 12),
    ]

    if report["empty"]:
        story.append(Paragraph("No records in this date range.", styles["Normal"]))
    else:
        summary = Table([[label, str(value)] for label, value in report["summary"]], hAlign="LEFT")
        summary.setStyle(TableStyle([("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                                     ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
        story += [summary, Spacer(1, 14)]

        data = [report["columns"]] + [[str(c) for c in row] for row in report["rows"]]
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
        ]))
        story.append(table)

    doc.build(story)
