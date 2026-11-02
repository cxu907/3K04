
# Simulated ADC messages
# these are just some simulated data to test the adc communication module 

def get_adc_messages():
    messages = [
        {
            "cabinet_id": "ADC-001",
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
    ]

    return messages
