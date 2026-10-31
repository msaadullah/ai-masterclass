import os
import requests
from dotenv import load_dotenv

load_dotenv()

sheet_url = os.environ.get("SHEET_URL")
if not sheet_url:
    raise SystemExit("SHEET_URL is missing. Add it to .env or set it in the environment.")

url = "https://api.open-meteo.com/v1/forecast?latitude=24.86&longitude=67.01&current_weather=true"

weather_response = requests.get(url, timeout=30)
weather_response.raise_for_status()
weather = weather_response.json().get("current_weather")
if weather is None:
    raise SystemExit("The weather API response did not contain current_weather.")

payload = {
    "city": "Karachi",
    "temperature": weather["temperature"],
    "windspeed": weather["windspeed"],
}
try:
    response = requests.post(sheet_url, json=payload, timeout=30)
except requests.RequestException as error:
    raise SystemExit(f"Could not connect to Apps Script: {error}") from None

if response.status_code == 401:
    raise SystemExit(
        "Apps Script returned HTTP 401 Unauthorized. Check its web app access "
        "settings and make sure SHEET_URL is the deployed /exec URL."
    )
if not response.ok:
    raise SystemExit(f"Apps Script returned HTTP {response.status_code}.")

print("Apps Script response:", response.status_code, response.text)
if response.text.strip() != "OK":
    raise SystemExit("The sheet script did not return OK: " + response.text)