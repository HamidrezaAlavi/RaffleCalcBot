import requests

TOKEN = "7740910314:AAEzgnRxolPt3h-El0PHdfJFYBvc9cqiGIU"
URL = "https://rafflecalcbot-production-46d1.up.railway.app/" + TOKEN

response = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={URL}")
print(response.json())
