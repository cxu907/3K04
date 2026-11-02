
# Health Monitoring Module

health = {}
it_notifications = {}


def updateHealthState(cabId, status):

    if status != "Online" and status != "Fault" and status != "Maintenance":
        print("Invalid health status")
        return False

    health[cabId] = status

    if status == "Fault":
        notifyIT(cabId)
    else:
        it_notifications[cabId] = False

    return True


def notifyIT(cabId):

    it_notifications[cabId] = True
    return True
