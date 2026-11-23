# Health Monitoring Module
#
# Hides the valid hardware health states, how they are stored and the fault policy.
#
# Interface:
#   updateHealthState(cabId, status) -> True / False (invalid status)
#       post: status stored; IT notified iff status == "Fault"
#   notifyIT(cabId)                  -> True
#   getAllHealth()                   -> list of dicts:
#       {"cabinet", "state", "it_notified"}

_health = {}
_it_notifications = {}


def updateHealthState(cabId, status):

    if status != "Online" and status != "Fault" and status != "Maintenance":
        print("Invalid health status")
        return False

    _health[cabId] = status

    if status == "Fault":
        notifyIT(cabId)
    else:
        _it_notifications[cabId] = False

    return True


def notifyIT(cabId):

    _it_notifications[cabId] = True
    return True


def getAllHealth():

    return [
        {"cabinet": cabId, "state": status, "it_notified": _it_notifications[cabId]}
        for cabId, status in _health.items()
    ]
