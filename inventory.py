
# Inventory Management Module

inventory = {}
pharmacist_notifications = {}
LOW_STOCK_LIMIT = 10


def updateStock(cabId, medId, quantity):

    medication_key = (cabId, medId)
    inventory[medication_key] = quantity

    if checkLowStock(cabId, medId):
        notifyPharmacist(cabId, medId)
    else:
        pharmacist_notifications[medication_key] = False

    return True


def checkLowStock(cabId, medId):

    medication_key = (cabId, medId)
    quantity = inventory[medication_key]

    if quantity < LOW_STOCK_LIMIT:
        return True
    else:
        return False


def notifyPharmacist(cabId, medId):

    medication_key = (cabId, medId)
    pharmacist_notifications[medication_key] = True

    return True
