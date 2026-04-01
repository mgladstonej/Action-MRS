import streamlit as st
import pandas as pd
import random
import requests
import base64
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import streamlit.components.v1 as components

API = "585d31561eea5169971dc2855e5f297a"
s = requests.Session()

# 🎨 Background + TEXT COLORS
img = base64.b64encode(open("background.jpg", "rb").read()).decode()

st.markdown(f"""
<style>

/* 🌌 Background */
.stApp {{
    background: url(data:image/jpeg;base64,{img});
    background-size: cover;
}}

/* ✅ ONLY TEXT WHITE (not everything blindly) */
h1, h2, h3, h4, h5, h6, label, p, span {{
    color: white !important;
}}

/* 🎯 Selectbox (closed) */
.stSelectbox > div > div {{
    background: rgba(0,0,0,0.6) !important;
    border: 2px solid cyan;
    border-radius: 10px;
    color: white !important;
    font-weight: bold;
    box-shadow: 0 0 15px cyan;
}}

/* 🔥 Dropdown popup FIX */
div[data-baseweb="popover"] {{
    background: #121212 !important;
}}

div[data-baseweb="option"] {{
    color: white !important;
    background: #121212 !important;
}}

div[data-baseweb="option"]:hover {{
    background: cyan !important;
    color: black !important;
}}

div[aria-selected="true"] {{
    background: #00f2ff !important;
    color: black !important;
}}

/* 🎛 Slider text fix */
.stSlider label {{
    color: white !important;
}}

/* 🚀 Button */
.stButton button {{
    background: linear-gradient(90deg,#00f2ff,#0077ff);
    color: white !important;
    border-radius: 10px;
    box-shadow: 0 0 18px cyan;
}}

</style>
""", unsafe_allow_html=True)

# 📊 Load + model
@st.cache_data
def load():
    m = pd.read_csv("movies.csv")

    ott = ["Netflix","Prime","Hotstar","HBO Max","Hulu","Apple TV+","YouTube","Jio Cinema"]

    m["rating"] = m.get("rating", [round(random.uniform(6,9.8),1) for _ in range(len(m))])
    m["duration"] = m.get("duration", [random.randint(90,180) for _ in range(len(m))])
    m["platform"] = m.get("platform", [random.choice(ott) for _ in range(len(m))])

    m["tags"] = m["genres"].fillna("") + " " + m["description"].fillna("")

    sim = cosine_similarity(
        CountVectorizer(stop_words="english").fit_transform(m["tags"])
    )

    return m, sim

movies, sim = load()

# 🎬 Poster
def poster(t):
    try:
        q = t.split("(")[0].split("-")[0].strip()
        r = s.get(
            f"https://api.themoviedb.org/3/search/movie?api_key={API}&query={q}",
            timeout=4
        ).json()

        if r.get("results") and r["results"][0].get("poster_path"):
            return f"https://image.tmdb.org/t/p/w300{r['results'][0]['poster_path']}"
    except:
        pass

    return "https://via.placeholder.com/300x450?text=No+Poster"

# 🤖 Recommend
def rec(name, n):
    if name not in movies["title"].values:
        return []

    i = movies[movies["title"] == name].index[0]
    idx = sorted(range(len(sim[i]),), key=lambda x: sim[i][x], reverse=True)

    return [movies.iloc[j] for j in idx[:n]]

# UI
st.title("🎬 ᗩҁ₮Į◎₪")
st.subheader("AI Powered Movie Recommender 🍿")

movie = st.selectbox("🔍 Select Movie", [""] + list(movies["title"]))
n = st.slider("🎯 Number of Recommendations", 5, 25, 10, 5)

# 🚀 Generate
if st.button("🚀 GENERATE"):
    res = rec(movie, n)

    if not res:
        st.warning("⚠ Select a movie.")
    else:
        html = """
        <style>
        .grid {display:grid;grid-template-columns:repeat(5,1fr);gap:20px}
        .card {position:relative;text-align:center}
        .poster {width:100%;border-radius:10px}
        .overlay {
            position:absolute;top:0;width:100%;height:100%;
            background:rgba(0,0,0,.8);
            opacity:0;padding:10px;color:white;font-size:12px
        }
        .card:hover .overlay {opacity:1}
        </style>
        <div class='grid'>
        """

        for m in res:
            p = poster(m["title"])
            d = m["description"][:180] + "..." if len(m["description"]) > 180 else m["description"]

            html += f"""
            <div class='card'>
                <img class='poster' src='{p}'>
                <div class='overlay'>
                    ⭐ {m['rating']}<br>
                    ⏳ {m['duration']} mins<br>
                    📺 {m['platform']}<br><br>
                    {d}
                </div>
                <div style='color:white'>{m['title']}</div>
            </div>
            """

        html += "</div>"

        components.html(html, height=1100)