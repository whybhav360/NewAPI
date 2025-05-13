# Apricot Production Forecast API 🍑

This FastAPI backend provides crop production forecasts (e.g., for apricots) based on the selected country. It returns both:

- A **Base64-encoded graph image** of historical and future predictions.
- A **dictionary of production values** (e.g., 2020, 2025).
- An optional **summary message**.

---

## 🚀 Features

- 🌐 Accepts a POST request with a country name.
- 📊 Returns predicted crop production values.
- 🖼️ Sends a graph image encoded as Base64.
- 🧠 Can be connected with mobile or web apps.

---

## 📦 API Endpoint

### `/predict`  
**Method**: `POST`  
**Content-Type**: `application/json`

#### ✅ Request Body:
```json
{
  "country": "India"
}
📤 Response:
```
``` Response
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "message": "In 2020, apricot production was 14,250 tons. In 2025, it is predicted to be 16,390 tons.",
  "production_data": {
    "2020": 14250.0,
    "2025": 16390.0
  }
}
```

🛠️ Setup Instructions
1. Clone this repo
bash
Copy
Edit
git clone https://github.com/whybhav360/ApriForecast.git
cd apricot-forecast-api
2. Create a virtual environment
bash
Copy
Edit
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
3. Install dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Run the app
bash
Copy
Edit
uvicorn main:app --reload
Open in browser:
http://127.0.0.1:8000/docs → Swagger UI

🧪 Example with cURL
bash
Copy
Edit
curl -X POST http://127.0.0.1:8000/predict \
-H "Content-Type: application/json" \
-d '{"country": "India"}'
🧠 Tech Stack
FastAPI

Pydantic

Uvicorn

Matplotlib (for graph generation)

📲 Compatible Frontends
This API can be used in:

Android apps (Kotlin + Retrofit)

Web apps (React, Vue, etc.)

CLI tools or other Python apps

✨ Future Improvements
Add support for more crop types.

Add authentication.

Add CSV upload for user data.

📄 License
MIT License

🤝 Contributing
Pull requests are welcome! For major changes, open an issue first to discuss what you’d like to change.

📬 Contact
Built with ❤️ by Vaibhav Madaan
