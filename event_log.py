# Event Log Module (Function 6 - Historical Data Management)
#
# Hides how records are stored and how record IDs are assigned.
# The log is append-only: records can be added and read, never edited or deleted.
#
# Interface:
#   addLog(recordType, cabId, details, timestamp=None) -> int (unique record id)
#       raises ValueError if the record is not well formed (nothing is stored)
#   searchLog(cabId=None, fromDate=None, toDate=None, recordType=None) -> list of dicts
#       {"id", "timestamp", "cabinet", "type", "details"}, oldest first
#       (a None filter means "any"; toDate is inclusive)

from datetime import datetime, date, time

RECORD_TYPES = ["Status", "Inventory", "Alarm", "Maintenance", "Health"]

_log = []
_next_id = 1


def addLog(recordType, cabId, details, timestamp=None):

    global _next_id

    if recordType not in RECORD_TYPES:
        raise ValueError(f"Invalid record type: {recordType}")
    if not isinstance(cabId, str) or not cabId:
        raise ValueError("Invalid cabinet id")
    if not isinstance(details, dict):
        raise ValueError("Log details must be a dict")

    record = {
        "id": _next_id,
        "timestamp": timestamp if timestamp is not None else datetime.now(),
        "cabinet": cabId,
        "type": recordType,
        "details": dict(details),
    }
    _log.append(record)
    _next_id += 1

    return record["id"]


def _start_of(value):

    if isinstance(value, datetime):
        return value
    return datetime.combine(value, time.min)


def _end_of(value):

    if isinstance(value, datetime):
        return value
    return datetime.combine(value, time.max)


def searchLog(cabId=None, fromDate=None, toDate=None, recordType=None):

    if fromDate is not None and toDate is not None:
        if _start_of(fromDate) > _end_of(toDate):
            raise ValueError("fromDate must not be after toDate")

    results = []

    for record in _log:
        if cabId is not None and record["cabinet"] != cabId:
            continue
        if recordType is not None and record["type"] != recordType:
            continue
        if fromDate is not None and record["timestamp"] < _start_of(fromDate):
            continue
        if toDate is not None and record["timestamp"] > _end_of(toDate):
            continue
        # copies, so callers (e.g. reports) can never change the stored log
        results.append({**record, "details": dict(record["details"])})

    return results
