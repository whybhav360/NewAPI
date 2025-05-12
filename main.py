from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from model import df, country_series, forecast_country, generate_forecast_image

app = FastAPI()

# CORS for frontend/Android access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/predict")
def predict(country: str = Query(..., description="Country name for prediction")):
    try:
        # Step 1: Get country time series
        series = country_series[country].dropna()

        # Step 2: Forecast
        forecast_df = forecast_country(series, country_name=country)
        if forecast_df is None:
            return JSONResponse(status_code=500, content={"error": "Forecasting failed."})

        # Step 3: Last 5 years historical data
        historical_data = series.last('5Y')

        # Step 4: Generate image
        img_base64 = generate_forecast_image(forecast_df, country_name=country, historical_data=historical_data)

        # Step 5: Send JSON response
        return {
            "forecast": forecast_df.to_dict(orient="records"),
            "image_base64": img_base64
        }

    except KeyError:
        return JSONResponse(status_code=404, content={"error": f"Country '{country}' not found."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
