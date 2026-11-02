# Inventory Management Module
#
# Hides how stock is stored and the low-stock policy.
#
# Interface:
#   updateStock(cabId, medId, quantity) -> True
#   checkLowStock(cabId, medId)         -> bool (False if item is unknown)
#   notifyPharmacist(cabId, medId)      -> True
#   getAllStock()                       -> list of dicts:
#       {"cabinet", "medication", "quantity", "low", "pharmacist_notified"}

_inventory = {}
_pharmacist_notifications = {}
LOW_STOCK_LIMIT = 10


def updateStock(cabId, medId, quantity):

    medication_key = (cabId, medId)
    _inventory[medication_key] = quantity

    if checkLowStock(cabId, medId):
        notifyPharmacist(cabId, medId)
    else:
        _pharmacist_notifications[medication_key] = False

    return True


def checkLowStock(cabId, medId):

    medication_key = (cabId, medId)
    quantity = _inventory.get(medication_key)

    if quantity is None:
        return False

    if quantity < LOW_STOCK_LIMIT:
        return True
    else:
        return False


def notifyPharmacist(cabId, medId):

    medication_key = (cabId, medId)
    _pharmacist_notifications[medication_key] = True

    return True


def getAllStock():

    records = []

    for (cabId, medId), quantity in _inventory.items():
        records.append({
            "cabinet": cabId,
            "medication": medId,
            "quantity": quantity,
            "low": checkLowStock(cabId, medId),
            "pharmacist_notified": _pharmacist_notifications[(cabId, medId)],
        })

    return records
