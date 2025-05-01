import os
import requests

API_KEY = os.getenv("oTg6i4DJisql8qwb_omKBPEAjJLh6VXeCCLnW9RchofSnyGJ-wzql6NemT2-sp4wduvvptc1bR9NjwvadpXfcviGOoR-80Rk2FV-9RTMPKma69rU1VPUmJQFMN5L8CY4xZoQPA")

def fetch_data_from_api():
    """Fetch data from an external API."""
    if not API_KEY:
        raise ValueError("API Key is missing!")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    url = "http://127.0.0.1:8000/"
    
    response = requests.get(url, headers=headers)
    
    return response.json() if response.status_code == 200 else {"error": "Failed to fetch data"}
