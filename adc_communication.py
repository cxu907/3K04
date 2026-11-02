
# ADC Communication Module

from adc_simulate import get_adc_messages
from inventory import updateStock
from health_manager import updateHealthState


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

    messages = get_adc_messages()
    adc_status = {}

    for message in messages:

        receive_message(message)

        cabinet_id = message["cabinet_id"]
        message_type = message["type"]
        data = message["data"]

        if message_type == "status":
            adc_status[cabinet_id] = data["status"]

        elif message_type == "inventory":
            updateStock(cabinet_id, data["medication"], data["quantity"])

        elif message_type == "health":
            updateHealthState(cabinet_id, data["state"])

    return adc_status
