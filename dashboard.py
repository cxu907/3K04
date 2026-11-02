# Dashboard Module
#
# Hides how information is displayed. Uses other modules only through
# their exported getters.
#
# Interface:
#   showDashboard(adc_status) -> None (prints the current state of the system)

from inventory import getAllStock
from health_manager import getAllHealth
from alarm_manager import getActiveAlarms, getMaintenanceNotes


def showDashboard(adc_status):

    print("\n===================================")
    print("  HOSPITAL ADC MONITORING SYSTEM")
    print("===================================")

    print("\nADC STATUS")
    print("-----------------------------------")

    for cabinet_id, status in adc_status.items():
        print(f"{cabinet_id}: {status}")
        if status == "Offline":
            print("COMMUNICATION LOST - data may be out of date")

    print("\nACTIVE ALARMS")
    print("-----------------------------------")

    alarms = getActiveAlarms()

    if not alarms:
        print("(none)")

    for cabinet_id, reason in alarms:
        print(f"{cabinet_id}: {reason}")

    print("\nMEDICATION INVENTORY")
    print("-----------------------------------")

    for item in getAllStock():

        print(f"\nCabinet: {item['cabinet']}")
        print(f"Medication: {item['medication']}")
        print(f"Quantity: {item['quantity']}")

        if item["low"]:
            print("LOW STOCK ALERT!")

        if item["pharmacist_notified"]:
            print("Pharmacist has been notified")

    print("\nHEALTH STATUS")
    print("-----------------------------------")

    for item in getAllHealth():

        print(f"\nCabinet: {item['cabinet']}")
        print(f"Health: {item['state']}")

        if item["it_notified"]:
            print("IT technician has been notified")

    print("\nMAINTENANCE NOTES")
    print("-----------------------------------")

    notes = getMaintenanceNotes()

    if not notes:
        print("(none)")

    for cabinet_id, description in notes:
        print(f"{cabinet_id}: {description}")

    print("\n===================================")
