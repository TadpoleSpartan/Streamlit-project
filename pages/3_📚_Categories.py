import streamlit as st
import json
from pathlib import Path
from json_utils import safe_load_json

st.set_page_config(page_title="Categories - Netherlands QuizMaster", page_icon="📚", layout="wide")

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
QUESTIONS_FILE = DATA_DIR / "questions.json"


def load_css():
    css_path = ROOT / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


from json_utils import safe_load_json

def load_questions():
    return safe_load_json(QUESTIONS_FILE, {"categories": {}})


load_css()

st.markdown(
    '''
    <div class="topbar">
        <div class="brand">
            <div class="logo">🇳🇱</div>
            <div>
                <div class="title">Netherlands QuizMaster</div>
                <div class="subtitle">Choose a category</div>
            </div>
        </div>
        <div class="nav-links">
            <button class="nav-link" onclick="window.location.href = window.location.origin + window.location.pathname + '?page=Home'">🏠 Home</button>
            <button class="nav-link" onclick="window.location.href = window.location.origin + window.location.pathname + '?page=2_🏆_Highscores'">🏆 Leaderboard</button>
            <button class="nav-link" onclick="window.location.href = window.location.origin + window.location.pathname + '?page=3_📚_Categories'">📚 Categories</button>
            <button class="nav-link" onclick="window.location.href = window.location.origin + window.location.pathname + '?page=4_⚙️_Settings'">⚙️ Settings</button>
        </div>
    </div>
    <div class="flag-stripe"></div>
    ''',
    unsafe_allow_html=True,
)

# notify when data updated
if st.session_state.get("questions_updated"):
    st.info("Question data changed; categories refreshed.")
    st.session_state.questions_updated = False

st.markdown("<h1 style='margin-bottom: 8px; font-weight: 600;'>Categories</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #6b7684; margin-bottom: 24px;'>Choose a topic to test your knowledge</p>", unsafe_allow_html=True)

data = load_questions()
categories = data.get("categories", {})

# Category information
category_info = {
    "Netherlands Geography": {"emoji": "🗺️", "description": "Cities, borders & landscape", "fun_fact": "No natural mountains exists"},
    "Dutch Culture & History": {"emoji": "🧀", "description": "Traditions, food & history", "fun_fact": "Koningsdag celebration"},
    "Famous Dutch People": {"emoji": "⭐", "description": "Artists, explorers & icons", "fun_fact": "Rembrandt & Van Gogh"},
    "Dutch Food": {"emoji": "🍽️", "description": "Local snacks and dishes", "fun_fact": "Stroopwafels from Gouda"},
    "World Foods": {"emoji": "🌏", "description": "Popular global dishes", "fun_fact": "Diversity of flavors"},
    "Dutch Festivals & Traditions": {"emoji": "🎊", "description": "Festivals, holidays & customs", "fun_fact": "Rich celebration culture"}
}

if categories:
    for name, questions_list in categories.items():
        info = category_info.get(name, {"emoji": "❓", "description": name, "fun_fact": ""})

        # compute stats
        total_points = 0
        for q in questions_list:
            total_points += q.get("points", 0)

        st.markdown(f"""
        <div style='background: var(--card); border: 1px solid rgba(255,255,255,0.08); border-radius: 9px; padding: 20px; margin-bottom: 16px;'>
            <div style='display: flex; align-items: start; justify-content: space-between;'>
                <div>
                    <h3 style='margin: 0 0 8px 0; font-weight: 600; font-size: 18px;'>{info['emoji']} {name}</h3>
                    <p style='margin: 0 0 12px 0; color: #6b7684; font-size: 13px;'>{info['description']}</p>
                    <div style='display: flex; gap: 8px;'>
                        <span class='stat-pill'>{len(questions_list)} questions</span>
                        <span class='stat-pill'>{total_points} points</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(2)
        with cols[0]:
            if st.button(f"Start Quiz", key=f"play_{name}", use_container_width=True):
                if not st.session_state.get("player_name"):
                    st.warning("Please enter your name on the Home page first.")
                else:
                    st.session_state.selected_category = name
                    st.switch_page("pages/1_🎮_Quiz.py")
        with cols[1]:
            if st.button(f"Preview", key=f"preview_{name}", use_container_width=True):
                with st.expander(f"Sample questions", expanded=False):
                    for idx, q in enumerate(questions_list[:3], 1):
                        st.write(f"**Q{idx}:** {q['question']}")

        st.markdown("")
else:
    st.warning("No categories found. Add questions to data/questions.json")

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("⌂ Home", use_container_width=True):
        st.switch_page("Home.py")
with col2:
    if st.button("🏆 Leaderboard", use_container_width=True):
        st.switch_page("pages/2_🏆_Highscores.py")
