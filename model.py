import pandas as pd
import numpy as np
from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
import warnings
import io
import base64
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=FutureWarning)

# Load the dataset and clean it
def load_data():
    df = pd.read_csv('Processed.csv')
    df.columns = df.columns.str.strip()  # Clean column names
    df = df.dropna(subset=['year', 'country', 'apricot'])  # Remove incomplete rows
    df['year'] = pd.to_datetime(df['year'], format='%Y', errors='coerce')
    df = df.dropna(subset=['year'])  # Drop invalid dates
    df = df.set_index('year').sort_index()
    return df

# Forecasting function
def forecast_country(series, country_name, forecast_years=5):
    try:
        series.index = pd.to_datetime(series.index, errors='coerce')
        series = series.asfreq('YS')  # Set frequency to Year Start
        series = series.dropna().sort_index()
        series = series.interpolate().ffill().bfill()

        # ARIMA model
        model = auto_arima(series, seasonal=False, trace=False, suppress_warnings=True)
        final_model = ARIMA(series, order=model.order)
        model_fit = final_model.fit()

        # Forecasting
        forecast = model_fit.get_forecast(steps=forecast_years)

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

# Plotting function to create image
def generate_forecast_image(forecast_df, country_name, historical_data):
    plt.figure(figsize=(8, 6))
    plt.plot(historical_data.index.year, historical_data.values, label='Historical Data', marker='o', color='blue')
    plt.plot(forecast_df['year'], forecast_df['predicted_apricot_growth'],
             label='Forecast (Next 5 Years)', marker='o', color='orange')
    plt.fill_between(forecast_df['year'],
                     forecast_df['lower_ci'],
                     forecast_df['upper_ci'],
                     color='orange', alpha=0.2)

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

# Initialize the data
df = load_data()
country_series = df.pivot(columns='country', values='apricot')
