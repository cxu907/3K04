import adc_simulate
from adc_communication import fetch_adc_messages, getAllAdcStatus
from dashboard import showDashboard
from datetime import date, datetime, timedelta
from report import generateReport, exportReport, formatReport

MENU = """
------------- DEMO MENU -------------
 1. Update ADC messages
 2. Show dashboard
 3. LOW stock
 4. RESTOCK
 5. Hardware FAULT
 6. Health ONLINE (clear fault)
 7. Raise alarm
 8. Connection LOSS
 9. RESTORE connection
10. BAD message
11. Generate REPORT
 0. Quit
--------------------------------------"""


def ask(prompt, default):

    value = input(f"{prompt} [{default}]: ").strip()

    if value:
        return value
    return default


def inject(cabinet_id, message_type, data):

    adc_simulate.inject_message({
        "cabinet_id": cabinet_id,
        "type": message_type,
        "data": data
    })
    print("Message queued. Choose 'Poll' to process it.")


adc_simulate.load_default_messages()
fetch_adc_messages()

showDashboard()

while True:

    print(MENU)
    choice = input("Choose: ").strip()

    if choice == "0":
        break

    elif choice == "1":
        fetch_adc_messages()

    elif choice == "2":
        showDashboard()

    elif choice == "3":
        cabinet = ask("Cabinet id", "ADC-001")
        inject(cabinet, "inventory", {"medication": ask("Medication", "Tylenol"), "quantity": 3})

    elif choice == "4":
        cabinet = ask("Cabinet id", "ADC-001")
        inject(cabinet, "inventory", {"medication": ask("Medication", "Tylenol"), "quantity": 50})

    elif choice == "5":
        inject(ask("Cabinet id", "ADC-001"), "health", {"state": "Fault"})

    elif choice == "6":
        inject(ask("Cabinet id", "ADC-001"), "health", {"state": "Online"})

    elif choice == "7":
        cabinet = ask("Cabinet id", "ADC-001")
        inject(cabinet, "alarm", {
            "reason": ask("Reason", "Door left open")
        })

    elif choice == "8":
        adc_simulate.set_connected(False)
        print("Connection dropped. Poll to see the system react.")

    elif choice == "9":
        adc_simulate.set_connected(True)
        for cabinet_id in getAllAdcStatus:
            inject(cabinet_id, "status", {"status": "Online"})
        fetch_adc_messages()

    elif choice == "10":
        adc_simulate.inject_message({
            "cabinet_id": "ADC-001",
            "type": "inventory",
            "data": {"medication": "Tylenol"}
        })
        print("Malformed message queued (missing quantity). Choose 'Poll'.")

    elif choice == "11":
        report_type = ask("Report type (Usage/Downtime/Alarm)", "Usage")
        start = ask("From date YYYY-MM-DD", str(date.today()))
        end = ask("To date YYYY-MM-DD", str(date.today()))
        try:
            report = generateReport(report_type,
                                    datetime.strptime(start, "%Y-%m-%d").date(),
                                    datetime.strptime(end, "%Y-%m-%d").date())
            print(formatReport(report))
            export_format = ask("Export (CSV/PDF/none)", "none")
            if export_format.lower() != "none":
                print("Saved to", exportReport(report, export_format))
        except Exception as error:
            print("Report error:", error)

    else:
        print("Unknown option")
