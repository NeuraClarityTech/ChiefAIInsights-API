# requirements.txt addition

# In your code
import httpx

async def read_google_sheet(sheet_id: str):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}"
    # Use API key authentication (simpler than OAuth)
    params = {"key": "YOUR_API_KEY"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        return response.json()
