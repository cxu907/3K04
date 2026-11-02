from adc_communication import fetch_adc_messages
from dashboard import showDashboard

adc_status = fetch_adc_messages()

showDashboard(adc_status)
