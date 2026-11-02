
# Dashboard Module

from inventory import inventory, checkLowStock, pharmacist_notifications
from health_manager import health, it_notifications


def showDashboard(adc_status):

    print("\n===================================")
    print("  HOSPITAL ADC MONITORING SYSTEM")
    print("===================================")

    print("\nADC STATUS")
    print("-----------------------------------")

    for cabinet_id, status in adc_status.items():
        print(f"{cabinet_id}: {status}")

    print("\nMEDICATION INVENTORY")
    print("-----------------------------------")

    for medication_key, quantity in inventory.items():

        cabinet_id, medication = medication_key

        print(f"\nCabinet: {cabinet_id}")
        print(f"Medication: {medication}")
        print(f"Quantity: {quantity}")

        if checkLowStock(cabinet_id, medication):
            print("LOW STOCK ALERT!")

        if pharmacist_notifications[medication_key] == True:
            print("Pharmacist has been notified")

    print("\nHEALTH STATUS")
    print("-----------------------------------")

    for cabinet_id, status in health.items():

        print(f"\nCabinet: {cabinet_id}")
        print(f"Health: {status}")

        if it_notifications[cabinet_id] == True:
            print("IT technician has been notified")

    print("\n===================================")
