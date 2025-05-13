# model.py

import pandas as pd
import numpy as np
from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
import warnings
import io
import base64
import matplotlib.pyplot as plt
import os
import joblib

warnings.filterwarnings("ignore", category=FutureWarning)

# ------------------ LOAD AND CLEAN DATA ------------------

def load_data():
    df = pd.read_csv('Processed.csv')
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=['year', 'country', 'apricot'])
    df['year'] = pd.to_datetime(df['year'], format='%Y', errors='coerce')
    df = df.dropna(subset=['year'])
    df = df.set_index('year').sort_index()
    return df

df = load_data()
country_series = df.pivot(columns='country', values='apricot')

# ------------------ MODEL CACHING ------------------

trained_models = {}

def train_and_cache_models():
    global trained_models
    for country in country_series.columns:
        series = country_series[country].dropna()
        series.index = pd.to_datetime(series.index)
        series = series.asfreq('YS').interpolate().ffill().bfill()

        try:
            auto_model = auto_arima(series, seasonal=False, trace=False, suppress_warnings=True)
            arima_model = ARIMA(series, order=auto_model.order)
            fitted_model = arima_model.fit()

            trained_models[country] = {
                'model': fitted_model,
                'series': series
            }
            print(f"[INFO] Cached model for {country}")
        except Exception as e:
            print(f"[WARNING] Could not train model for {country}: {e}")

# Load from disk if available
if os.path.exists('trained_models.pkl'):
    trained_models = joblib.load(open('trained_models.pkl', 'rb'))
    print("[INFO] Loaded trained models from disk")
else:
    train_and_cache_models()
    joblib.dump(trained_models, 'trained_models.pkl')
    print("[INFO] Trained models saved to disk")

# ------------------ FORECAST FUNCTION ------------------

def forecast_country(series, country_name, forecast_years=5):
    try:
        model_data = trained_models.get(country_name)
        if model_data is None:
            raise ValueError(f"No trained model for {country_name}")

        fitted_model = model_data['model']
        series = model_data['series']

        forecast = fitted_model.get_forecast(steps=forecast_years)

        last_year = series.index[-1].year
        future_years = [last_year + i for i in range(1, forecast_years + 1)]

        return pd.DataFrame({
            'country': country_name,
            'year': future_years,
            'predicted_apricot_growth': forecast.predicted_mean.values,
            'lower_ci': forecast.conf_int().iloc[:, 0].values,
            'upper_ci': forecast.conf_int().iloc[:, 1].values
        })
    except Exception as e:
        print(f"[ERROR] Forecast failed for {country_name}: {e}")
        return None

# ------------------ PLOT GENERATION ------------------

def generate_forecast_image(forecast_df, country_name, historical_data):
    plt.figure(figsize=(8, 6))
    historical_data = historical_data.last('5Y')
    historical_data.index = pd.to_datetime(historical_data.index)

    # Combine historical and forecast
    all_years = list(historical_data.index.year) + list(forecast_df['year'])
    all_values = list(historical_data.values) + list(forecast_df['predicted_apricot_growth'])

    # Plot the full line (historical + forecast)
    plt.plot(all_years, all_values, color='blue', marker='o')

    # Overwrite forecast section in orange
    plt.plot(forecast_df['year'], forecast_df['predicted_apricot_growth'],
             label='Forecast (Next 5 Years)', color='orange', marker='o')
    
    # Confidence interval
    plt.fill_between(forecast_df['year'],
                     forecast_df['lower_ci'],
                     forecast_df['upper_ci'],
                     color='orange', alpha=0.2, label='Confidence Interval')

    plt.title(f'Apricot Production Forecast - {country_name}')
    plt.xlabel('Year')
    plt.ylabel('Apricot Production')
    plt.legend()
    plt.grid(True)
    plt.xticks(list(historical_data.index.year) + list(forecast_df['year']), rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return img_base64
