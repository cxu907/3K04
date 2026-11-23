# Alarm Manager Module
#
# Hides how alarms and maintenance notes are stored and ordered.
#
# Interface:
#   recordAlarm(cabId, severity, reason) -> True / False (invalid severity)
#   getActiveAlarms()                    -> list of (cabId, severity, reason),
#                                           most severe first
#   recordMaintenance(cabId, description)-> True
#   getMaintenanceNotes()                -> list of (cabId, description)

_alarms = []
_maintenance = []


def recordAlarm(cabId, severity, reason):

    _alarms.append((cabId, reason))
    return True


def getActiveAlarms():

    return _alarms


def recordMaintenance(cabId, description):

    _maintenance.append((cabId, description))
    return True


def getMaintenanceNotes():

    return list(_maintenance)
