# Simulated ADC messages
# these are just some simulated data to test the adc communication module
#
# Simulates the link to the ADCs: messages are queued here and handed to
# the communication module, and the link can be dropped to test comm loss.
#
# Interface:
#   get_adc_messages()      -> list of queued messages (queue is emptied)
#                              raises ConnectionError if the link is down
#   load_default_messages() -> queue the sample messages
#   inject_message(message) -> queue one message (can be malformed on purpose)
#   set_connected(flag)     -> simulate the link going down / coming back

_queue = []
_connected = True


def get_adc_messages():

    global _queue

    if not _connected:
        raise ConnectionError("Connection to ADCs lost")

    messages = _queue
    _queue = []

    return messages


def load_default_messages():

    _queue.extend([
        {
            "cabinet_id": "ADC-001",
            "type": "status",
            "data": {"status": "Online"}
        },
        {
            "cabinet_id": "ADC-002",
            "type": "status",
            "data": {"status": "Online"}
        },
        {
            "cabinet_id": "ADC-001",
            "type": "inventory",
            "data": {"medication": "Tylenol", "quantity": 5}
        },
        {
            "cabinet_id": "ADC-002",
            "type": "alarm",
            "data": {
                "severity": "Critical",
                "reason": "Temperature too high"
            }
        },
        {
            "cabinet_id": "ADC-002",
            "type": "health",
            "data": {"state": "Fault"}
        },
        {
            "cabinet_id": "ADC-001",
            "type": "maintenance",
            "data": {"description": "Scheduled maintenance"}
        }
    ])


def inject_message(message):

    _queue.append(message)


def set_connected(flag):

    global _connected
    _connected = bool(flag)
