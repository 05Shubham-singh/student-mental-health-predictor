# 🧠 Student Mental Health Predictor

A machine learning project that estimates a student's **mental health score** (higher = better) from their social-media habits, lifestyle and stress level. It includes a trained Random Forest model, a FastAPI backend and an interactive Streamlit app with a speedometer-style result.

### 🚀 [Live demo → student-mental-health-predictor-sk.streamlit.app](https://student-mental-health-predictor-sk.streamlit.app/)

> ⚠️ **Disclaimer:** This project is for educational purposes only. It is not a medical or diagnostic tool.

---

## ✨ Features

- Interactive form split into **Profile**, **Social Media** and **Lifestyle** tabs
- One-click example students (Balanced, Typical, Heavy user)
- **Speedometer gauge** with colour zones and a risk label
- Personalised tips on screen time, sleep, activity and stress
- REST API (`POST /predict`) with input validation via Pydantic
- Full training notebook: cleaning, feature engineering, model comparison and tuning

## 🖼️ Result zones

| Score | Meaning |
|-------|---------|
| ≥ 7.5 | 🟢 Good mental well-being |
| 6.0 – 7.5 | 🟡 Moderate / stable |
| 4.5 – 6.0 | 🟠 At risk |
| < 4.5 | 🔴 High risk |

The scores in the training data range from roughly 3.6 to 9.4.

## 📊 Model

The pipeline is a scikit-learn `ColumnTransformer` feeding a `RandomForestRegressor`.

**Preprocessing**
- `Study_Hours`: log1p transform and scaling
- Other numeric columns: scaling
- `Stress_Level`: ordinal encoding (Low < Medium < High < Very High)
- Gender, Academic Level, Platform, Purpose of Use, Grouped Country: one-hot encoding
- `Grouped_Country`: the top 10 countries, with all others grouped as `Other`

**Results (test set)**

| Model | R² | MAE | RMSE |
|-------|----|-----|------|
| Linear Regression | 0.722 | – | – |
| **Random Forest (default, deployed)** | **0.878** | 0.347 | 0.464 |
| Random Forest (tuned) | 0.865 | 0.369 | 0.487 |

The default Random Forest was saved as `Mental_Helath_Model.pkl`. The tuned version generalised slightly better (smaller train–test gap) but scored lower on the test set.

## 🗂️ Project structure

```
.
├── app.py                    # Streamlit UI
├── main.py                   # FastAPI backend
├── main.ipynb                # Training notebook
├── Mental_Helath_Model.pkl   # Trained pipeline
├── requirements.txt
└── README.md
```

## 🧾 Inputs

| Field | Type / allowed values |
|-------|-----------------------|
| `age` | integer, 10–100 |
| `gender` | Male, Female |
| `country` | text |
| `academic_level` | High School, Undergraduate, Graduate |
| `most_use_platform` | Facebook, LinkedIn, Instagram, Snapchat, Twitter, YouTube, TikTok, LINE, KakaoTalk, VKontakte, WhatsApp, WeChat |
| `purpose_of_use` | Networking, Education, Entertainment, News |
| `avg_daily_usage_hours` | float, 0–24 |
| `daily_unlocks` | integer, ≥ 0 |
| `study_hours` | float, 0–24 |
| `physical_activity_hours` | float, 0–24 |
| `sleep_hours_per_night` | float, 0–24 |
| `stress_level` | Low, Medium, High, Very High |

## ⚙️ Run locally

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Start the API** (terminal 1, in the folder that contains `Mental_Helath_Model.pkl`)

```bash
uvicorn main:app --reload
```

Interactive API docs are available at http://127.0.0.1:8000/docs.

**3. Start the Streamlit app** (terminal 2)

```bash
streamlit run app.py
```

Open http://localhost:8501. If your API runs on a different port, change the **API endpoint** in the sidebar.

### Example API request

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 21,
    "gender": "Female",
    "country": "India",
    "academic_level": "Undergraduate",
    "most_use_platform": "Instagram",
    "purpose_of_use": "Entertainment",
    "avg_daily_usage_hours": 5.0,
    "daily_unlocks": 170,
    "study_hours": 3.0,
    "physical_activity_hours": 1.7,
    "sleep_hours_per_night": 6.6,
    "stress_level": "Medium"
  }'
```

Response:

```json
{ "predicted_mental_health_score": 6.8 }
```

## 🛠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| `Could not reach the API` | Make sure `uvicorn main:app --reload` is running and the sidebar endpoint matches its port |
| `FileNotFoundError: Mental_Helath_Model.pkl` | Start uvicorn from the folder that contains the `.pkl` file |
| `No module named 'plotly'` | `pip install plotly` (use `python -m pip` if you have several Python installs) |
| `use_container_width` warning | Update to the latest `app.py`, which uses `width="stretch"` |

## 🧰 Tech stack

Python · pandas · scikit-learn · joblib · FastAPI · Pydantic · Uvicorn · Streamlit · Plotly

## ⚠️ Limitations

- The model is trained on a limited survey dataset, and predictions reflect patterns in that data only.
- The score is an estimate and should not be used for diagnosis or treatment decisions.
- Results may be less reliable for countries or groups that are under-represented in the data.

## 👤 Author

Built by **Shubham Singh**. Feedback and suggestions are welcome.
