# ADC Communication Module
#
# Receives ADC messages, checks them and routes them to the right module.
# Hides the message format and the communication-loss behaviour.
#
# Interface:
#   fetch_adc_messages() -> dict {cabinet_id: status}
#       Never raises: malformed messages are rejected and reported;
#       if the link to the ADCs is down, every known cabinet is marked "Offline".
#
# "status" = connectivity of the cabinet (Online/Offline).
# "health" (health_manager) = hardware state (Online/Fault/Maintenance).

from adc_simulate import get_adc_messages
from inventory import updateStock
from health_manager import updateHealthState
from alarm_manager import recordAlarm, recordMaintenance

adc_status = {}

REQUIRED_DATA = {
    "status": ["status"],
    "inventory": ["medication", "quantity"],
    "alarm": ["severity", "reason"],
    "health": ["state"],
    "maintenance": ["description"],
}


def is_valid_message(message):

    if not isinstance(message, dict):
        return False

    for key in ["cabinet_id", "type", "data"]:
        if key not in message:
            return False

    if message["type"] not in REQUIRED_DATA:
        return False

    if not isinstance(message["data"], dict):
        return False

    for field in REQUIRED_DATA[message["type"]]:
        if field not in message["data"]:
            return False

    if message["type"] == "inventory":
        quantity = message["data"]["quantity"]
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 0:
            return False

    return True


def receive_message(message):

    cabinet_id = message["cabinet_id"]
    message_type = message["type"]
    data = message["data"]

    print(f"\nMessage from {cabinet_id}:")
    print(f"Type of Alert: {message_type}")

    if message_type == "status":
        print(f"Status: {data['status']}")

    elif message_type == "inventory":
        print(f"Medication: {data['medication']}")
        print(f"Quantity: {data['quantity']}")

    elif message_type == "alarm":
        print(f"Severity: {data['severity']}")
        print(f"Reason: {data['reason']}")

    elif message_type == "health":
        print(f"Health: {data['state']}")

    elif message_type == "maintenance":
        print(f"Description: {data['description']}")

    else:
        print("Error: Invalid message type")


def fetch_adc_messages():

    try:
        messages = get_adc_messages()
    except ConnectionError:
        print("\nCOMMUNICATION LOSS: cannot reach the ADCs")
        for cabinet_id in adc_status:
            adc_status[cabinet_id] = "Offline"
        return adc_status

    for message in messages:

        if not is_valid_message(message):
            print(f"\nError: invalid message rejected: {message}")
            continue

        receive_message(message)

        cabinet_id = message["cabinet_id"]
        message_type = message["type"]
        data = message["data"]

        if message_type == "status":
            adc_status[cabinet_id] = data["status"]

        elif message_type == "inventory":
            updateStock(cabinet_id, data["medication"], data["quantity"])

        elif message_type == "alarm":
            if not recordAlarm(cabinet_id, data["severity"], data["reason"]):
                print("Error: invalid alarm severity, alarm rejected")

        elif message_type == "health":
            updateHealthState(cabinet_id, data["state"])

        elif message_type == "maintenance":
            recordMaintenance(cabinet_id, data["description"])

    return adc_status
