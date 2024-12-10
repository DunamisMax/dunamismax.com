from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
import httpx
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Load API key from environment variables
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "<YOUR_API_KEY>")


@router.get("")
async def get_weather_form(request: Request):
    return templates.TemplateResponse(
        "weather/weather.html", {"request": request, "weather_data": None}
    )


@router.post("")
async def post_weather(request: Request, zip_code: str = Form(...)):
    url = f"https://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&units=imperial&appid={OPENWEATHER_API_KEY}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Weather data not found")
        data = resp.json()

    weather_data = {
        "location": data.get("name"),
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"].title(),
    }
    return templates.TemplateResponse(
        "weather/weather.html", {"request": request, "weather_data": weather_data}
    )
