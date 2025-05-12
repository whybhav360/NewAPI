# main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from model import forecast_country, generate_forecast_image, country_series, df
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class CountryRequest(BaseModel):
    country: str

@app.get("/")
def root():
    return {"message": "Apricot Forecast API is running"}

@app.post("/predict")
def predict_apricot(request: CountryRequest):
    country = request.country.strip()
    
    if country not in country_series.columns:
        return {"error": f"No data available for country: {country}"}

    series = country_series[country].dropna()
    forecast_df = forecast_country(series, country)

    if forecast_df is None:
        return {"error": "Forecasting failed."}

    historical_data = df[df['country'] == country]['apricot'].last('5Y')
    historical_data.index = pd.to_datetime(historical_data.index)
    historical_data = historical_data.asfreq('YS').interpolate().ffill().bfill()

    image_base64 = generate_forecast_image(forecast_df, country, historical_data)

    return {
        "forecast": forecast_df.to_dict(orient="records"),
        "plot_image_base64": image_base64
    }

# For local testing
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
