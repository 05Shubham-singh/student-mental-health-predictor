import plotly.graph_objects as go
import requests
import streamlit as st

# ---------------------------------------------------------------
# Page config
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Student Mental Health Predictor",
    page_icon="🧠",
    layout="wide",
)

API_URL_DEFAULT = "https://student-mental-health-predictor-wpn3.onrender.com/predict"

COUNTRIES = [
    "India", "USA", "Canada", "Australia", "UK", "Germany", "Mexico",
    "Turkey", "France", "Brazil", "Japan", "China", "South Korea",
    "Russia", "Italy", "Spain", "Netherlands", "Sweden", "Other",
]
PLATFORMS = [
    "Facebook", "LinkedIn", "Instagram", "Snapchat", "Twitter", "YouTube",
    "TikTok", "LINE", "KakaoTalk", "VKontakte", "WhatsApp", "WeChat",
]

# ---------------------------------------------------------------
# Styling
# ---------------------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem;}
    .score-card {
        border-radius: 16px; padding: 28px; text-align: center;
        background: linear-gradient(135deg, #1f2937, #111827);
        border: 1px solid #374151;
    }
    .score-value {font-size: 4rem; font-weight: 800; line-height: 1;}
    .score-label {font-size: 1.2rem; margin-top: 8px; opacity: .9;}
    .hint {opacity: .7; font-size: .9rem;}
    .hero {
        border-radius: 18px; padding: 36px 32px; margin-bottom: 18px;
        background: linear-gradient(135deg, #4f46e5, #7c3aed 55%, #db2777);
        color: white;
    }
    .hero h1 {margin: 0 0 8px 0; font-size: 2.4rem; color: white;}
    .hero p {margin: 0; font-size: 1.1rem; opacity: .95;}
    .card {
        border-radius: 14px; padding: 18px; height: 100%;
        border: 1px solid #374151; background: rgba(127,127,127,.08);
    }
    .card h4 {margin: 0 0 6px 0;}
    </style>
    """,
    unsafe_allow_html=True,
)


def interpret(score: float):
    """Map the 0-10 style score to a label and colour."""
    if score >= 7.5:
        return "Good mental well-being", "#22c55e"
    if score >= 6.0:
        return "Moderate / stable", "#eab308"
    if score >= 4.5:
        return "At risk", "#f97316"
    return "High risk", "#ef4444"


def make_gauge(score: float, color: str) -> go.Figure:
    """Speedometer-style gauge, 0-10, with colour zones and a needle."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"size": 56, "color": color}, "valueformat": ".2f"},
        gauge={
            "axis": {"range": [0, 10], "tickvals": [0, 2, 4, 6, 8, 10],
                     "tickwidth": 2, "ticklen": 10},
            "bar": {"color": "rgba(0,0,0,0)", "thickness": 0},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 4.5], "color": "#ef4444"},
                {"range": [4.5, 6.0], "color": "#f97316"},
                {"range": [6.0, 7.5], "color": "#eab308"},
                {"range": [7.5, 10], "color": "#22c55e"},
            ],
            "threshold": {"line": {"color": "#f9fafb", "width": 6},
                          "thickness": 0.9, "value": score},
        },
    ))
    fig.update_layout(
        height=300, margin=dict(l=30, r=30, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)", font={"color": "#9ca3af"},
    )
    return fig


# ---------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    api_url = st.text_input("API endpoint", API_URL_DEFAULT)
    st.caption("Start the backend with:\n\n`uvicorn main:app --reload`")
    st.divider()
    st.markdown(
        "**About**\n\nThis tool uses a Random Forest model trained on a student "
        "social-media & mental-health dataset to estimate a mental health score "
        "(higher = better)."
    )
    st.warning(
        "For educational purposes only. This is not a medical or "
        "diagnostic tool.",
        icon="⚠️",
    )

# ---------------------------------------------------------------
# Header
# ---------------------------------------------------------------
st.markdown(
    """
    <div class='hero'>
        <h1>🧠 Student Mental Health Predictor</h1>
        <p>Estimate a student's mental health score from social-media habits,
        sleep, study time, activity and stress.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Model", "Random Forest")
m2.metric("Test R²", "0.878")
m3.metric("Test MAE", "0.35")
m4.metric("Inputs", "12 features")

PRESETS = {
    "Balanced": dict(age=21, avg_usage=3.0, unlocks=90, study=4.0, activity=1.5, sleep=7.5, stress="Low"),
    "Typical": dict(age=21, avg_usage=5.0, unlocks=170, study=3.0, activity=1.7, sleep=6.6, stress="Medium"),
    "Heavy user": dict(age=20, avg_usage=8.5, unlocks=300, study=1.5, activity=0.3, sleep=4.5, stress="Very High"),
}
DEFAULTS = PRESETS["Typical"]
if "preset" not in st.session_state:
    st.session_state.preset = "Typical"

st.markdown("##### ⚡ Quick start: load an example student")
pcols = st.columns(len(PRESETS))
for col, name in zip(pcols, PRESETS):
    if col.button(name, width="stretch"):
        st.session_state.preset = name
P = PRESETS[st.session_state.preset]
st.caption(f"Loaded example: **{st.session_state.preset}**. Adjust anything below, then click Predict.")

# ---------------------------------------------------------------
# Input form
# ---------------------------------------------------------------
with st.form("prediction_form"):
    tab_profile, tab_social, tab_life = st.tabs(
        ["👤 Profile", "📱 Social Media", "🏃 Lifestyle"]
    )

    with tab_profile:
        c1, c2 = st.columns(2)
        age = c1.number_input("Age", min_value=10, max_value=100, value=P['age'], step=1, key=f'age_{st.session_state.preset}')
        gender = c2.radio("Gender", ["Male", "Female"], horizontal=True)
        c3, c4 = st.columns(2)
        country = c3.selectbox("Country", COUNTRIES, index=0)
        academic_level = c4.selectbox(
            "Academic level", ["High School", "Undergraduate", "Graduate"], index=1
        )

    with tab_social:
        c1, c2 = st.columns(2)
        platform = c1.selectbox("Most used platform", PLATFORMS, index=2)
        purpose = c2.selectbox(
            "Main purpose of use",
            ["Entertainment", "Networking", "Education", "News"],
        )
        avg_usage = st.slider(
            "Average daily usage (hours)", 0.0, 24.0, P["avg_usage"], 0.1, key=f"u_{st.session_state.preset}"
        )
        unlocks = st.number_input(
            "Daily phone unlocks", min_value=0, max_value=1000, value=P["unlocks"], step=5, key=f"ul_{st.session_state.preset}"
        )

    with tab_life:
        c1, c2 = st.columns(2)
        study = c1.slider("Study hours per day", 0.0, 24.0, P["study"], 0.1, key=f"st_{st.session_state.preset}")
        activity = c2.slider("Physical activity (hours/day)", 0.0, 24.0, P["activity"], 0.1, key=f"ac_{st.session_state.preset}")
        sleep = c1.slider("Sleep hours per night", 0.0, 24.0, P["sleep"], 0.1, key=f"sl_{st.session_state.preset}")
        stress = c2.select_slider(
            "Stress level", options=["Low", "Medium", "High", "Very High"],
            value=P["stress"], key=f"sr_{st.session_state.preset}",
        )

    submitted = st.form_submit_button(
        "🔮 Predict", width="stretch", type="primary"
    )

# ---------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------
if submitted:
    payload = {
        "age": int(age),
        "gender": gender,
        "country": country,
        "academic_level": academic_level,
        "most_use_platform": platform,
        "purpose_of_use": purpose,
        "avg_daily_usage_hours": float(avg_usage),
        "daily_unlocks": int(unlocks),
        "study_hours": float(study),
        "physical_activity_hours": float(activity),
        "sleep_hours_per_night": float(sleep),
        "stress_level": stress,
    }

    try:
        with st.spinner("Analyzing..."):
            resp = requests.post(api_url, json=payload, timeout=15)
        resp.raise_for_status()
        score = resp.json()["predicted_mental_health_score"]
    except requests.exceptions.ConnectionError:
        st.error("Could not reach the API. Is `uvicorn main:app --reload` running?")
        st.stop()
    except requests.exceptions.HTTPError:
        st.error(f"API returned an error ({resp.status_code}): {resp.text}")
        st.stop()
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        st.stop()

    label, color = interpret(score)

    st.divider()
    left, right = st.columns([1, 1.4], gap="large")

    with left:
        st.plotly_chart(make_gauge(score, color), width="stretch",
                        config={"displayModeBar": False})
        st.markdown(
            f"<div style='text-align:center;font-size:1.4rem;font-weight:700;"
            f"color:{color}'>{label}</div>",
            unsafe_allow_html=True,
        )
        st.caption("Scale in training data: roughly 3.6 (low) to 9.4 (high).")

    with right:
        st.subheader("💡 Insights")
        tips = []
        if avg_usage > 6:
            tips.append("📵 Daily social media usage is high. Try screen-time limits.")
        if unlocks > 220:
            tips.append("🔓 Frequent phone unlocks. Consider notification batching.")
        if sleep < 6:
            tips.append("😴 Sleep is below 6 hours. Aim for 7–9 hours.")
        if activity < 1:
            tips.append("🏃 Low physical activity. Even a 20-minute walk helps.")
        if stress in ("High", "Very High"):
            tips.append("🧘 Stress is elevated. Consider relaxation techniques or "
                        "talking to a counselor.")
        if not tips:
            tips.append("✅ Habits look balanced. Keep it up!")
        for t in tips:
            st.info(t)

        with st.expander("View submitted data"):
            st.json(payload)

if not submitted:
    st.divider()
    st.subheader("How it works")
    a, b, c = st.columns(3)
    a.markdown("<div class='card'><h4>1️⃣ Enter details</h4>Fill in profile, social-media and lifestyle tabs, or load an example.</div>", unsafe_allow_html=True)
    b.markdown("<div class='card'><h4>2️⃣ Predict</h4>The form is sent to the FastAPI <code>/predict</code> endpoint running your trained model.</div>", unsafe_allow_html=True)
    c.markdown("<div class='card'><h4>3️⃣ Review</h4>See the score, a risk label and tailored tips on sleep, screen time and stress.</div>", unsafe_allow_html=True)