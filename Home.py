import streamlit as st
import json
from pathlib import Path
import random
from json_utils import ensure_json_file, safe_load_json

# Basic page setup
st.set_page_config(page_title="Netherlands QuizMaster", page_icon="🎯", layout="wide")

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
QUESTIONS_FILE = DATA_DIR / "questions.json"

# Initialize JSON files on app startup
DATA_DIR.mkdir(parents=True, exist_ok=True)
ensure_json_file(QUESTIONS_FILE, {"categories": {}})
ensure_json_file(DATA_DIR / "highscores.json", {"scores": []})


def load_css():
    css_path = ROOT / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


from json_utils import safe_load_json

def load_questions():
    return safe_load_json(QUESTIONS_FILE, {"categories": {}})


def get_categories():
    return list(load_questions().get("categories", {}).keys())


load_css()

# Page container for consistent layout
st.markdown('<div class="container">', unsafe_allow_html=True)
# if editor signaled an update, notify
if st.session_state.get("questions_updated"):
    st.info("Questions database updated; new data will be used going forward.")
    st.session_state.questions_updated = False

# Session defaults
if "player_name" not in st.session_state:
    st.session_state.player_name = ""
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None
if "total_games" not in st.session_state:
    st.session_state.total_games = 0
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "best_streak" not in st.session_state:
    st.session_state.best_streak = 0
if "selected_difficulty" not in st.session_state:
    st.session_state.selected_difficulty = "Medium"
if "difficulty_selector_active" not in st.session_state:
    st.session_state.difficulty_selector_active = False

st.markdown(
        '''
        <div class="topbar">
            <div class="brand">
                <div class="logo">🇳🇱</div>
                <div>
                    <div class="title">Netherlands QuizMaster</div>
                    <div class="subtitle">Test your knowledge on Dutch culture, history, and more</div>
                </div>
            </div>
            <div class="nav-links">
                <button class="nav-link" onclick="window.location.href = window.location.origin + window.location.pathname + '?page=Home'">🏠 Home</button>
                <button class="nav-link" onclick="window.location.href = window.location.origin + window.location.pathname + '?page=2_🏆_Highscores'">🏆 Leaderboard</button>
                <button class="nav-link" onclick="window.location.href = window.location.origin + window.location.pathname + '?page=3_📚_Categories'">📚 Categories</button>
                <button class="nav-link" onclick="window.location.href = window.location.origin + window.location.pathname + '?page=4_⚙️_Settings'">⚙️ Settings</button>
                <button class="nav-link" onclick="window.location.href = window.location.origin + window.location.pathname + '?page=6_💬_Chat'">💬 Chat</button>
            </div>
        </div>
        <div class="hero">
            <h1>Sharpen your knowledge of the Netherlands</h1>
            <p>Engaging quizzes, progress tracking, and meaningful achievements — built to help you learn.</p>
        </div>
        ''',
        unsafe_allow_html=True,
)

st.markdown('<div class="flag-stripe"></div>', unsafe_allow_html=True)

st.markdown("---")

# Player input section
col1, col2 = st.columns([3, 1])
with col1:
    name = st.text_input("Your name", value=st.session_state.player_name, placeholder="Enter your name to start", label_visibility="collapsed")
    if name:
        st.session_state.player_name = name
with col2:
    st.write("")
    if st.session_state.player_name:
        st.markdown(f"<div class='stat-pill' style='background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); color: #3fb950; font-weight: 600;'>✓ {st.session_state.player_name}</div>", unsafe_allow_html=True)
        # Level display and controls
        lvl = st.session_state.get("level", 1)
        st.markdown(f"<div style='margin-top:8px;'><span class='badge'>Level {lvl}</span></div>", unsafe_allow_html=True)
        if st.button("Reset Level", key="reset_level_btn"):
            st.session_state.level = 1
            st.success("Level reset to 1")
        st.session_state.level_mode = st.checkbox("Enable Level Progression", value=st.session_state.get("level_mode", True))

st.markdown("---")

# Category cards
categories = get_categories()

category_descriptions = {
    "Netherlands Geography": "🗺️ Cities, borders, and landscapes",
    "Dutch Culture & History": "🧀 Traditions, art, and history",
    "Famous Dutch People": "⭐ Artists, explorers, and heroes",
    "Dutch Food": "🍽️ Tastes of the Netherlands",
    "World Foods": "🌎 Famous dishes from around the world",
    "Dutch Festivals & Traditions": "🎊 Celebrations and customs"
}

st.markdown("### Choose a Category")
if categories:
    # Difficulty selector (shown when a category is selected and difficulty_selector_active is True)
    if st.session_state.difficulty_selector_active and st.session_state.selected_category:
        st.markdown(f"<p style='color: #6b7684; margin-bottom: 12px; font-size: 13px;'>Playing: <strong>{st.session_state.selected_category}</strong></p>", unsafe_allow_html=True)
        st.markdown("**Select Difficulty:**")
        difficulty_cols = st.columns(4)
        difficulties = ["Easy", "Medium", "Hard", "Mixed"]
        for idx, diff in enumerate(difficulties):
            with difficulty_cols[idx]:
                diff_icon = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴", "Mixed": "🎲"}.get(diff, "")
                if st.button(f"{diff_icon} {diff}", use_container_width=True, key=f"diff_{diff}"):
                    st.session_state.selected_difficulty = diff
                    st.session_state.total_games += 1
                    st.balloons()
                    st.switch_page("pages/1_🎮_Quiz.py")
        
        st.markdown("---")
        if st.button("← Back to Categories", use_container_width=True):
            st.session_state.difficulty_selector_active = False
            st.rerun()
    else:
        # Show category cards
        st.markdown('<div class="category-grid">', unsafe_allow_html=True)
        for cat in categories:
            desc = category_descriptions.get(cat, "Test your knowledge")
            st.markdown(f"<div class='category-card'><h3 style='margin: 0 0 8px 0; font-weight: 500; font-size: 16px;'>{cat}</h3><p class='muted' style='margin: 0; font-size: 13px;'>{desc}</p></div>", unsafe_allow_html=True)
            if st.button(f"Play", key=f"play_{cat}", use_container_width=True):
                if not st.session_state.player_name:
                    st.warning("Please enter your name first.")
                else:
                    st.session_state.selected_category = cat
                    st.session_state.difficulty_selector_active = True
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("No categories found. Add questions to `data/questions.json`")

st.markdown("---")
st.markdown("### Fun Fact")
facts = [
    "🚲 There are more bicycles than people in the Netherlands!",
    "🥞 Stroopwafels were invented in Gouda.",
    "🌊 Dutch dikes protect large areas of land below sea level.",
    "🧀 The Netherlands exports more cheese than any other country.",
    "🌷 Tulips are not native to the Netherlands but are iconic there.",
]
st.markdown(f"<div class='stat-pill'>{random.choice(facts)}</div>", unsafe_allow_html=True)

st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🏆 Leaderboard", use_container_width=True):
        st.switch_page("pages/2_🏆_Highscores.py")
with col2:
    if st.button("📚 Categories", use_container_width=True):
        st.switch_page("pages/3_📚_Categories.py")
with col3:
    if st.button("⚙️ Settings", use_container_width=True):
        st.switch_page("pages/4_⚙️_Settings.py")
with col4:
    if st.button("ℹ️ About", use_container_width=True):
        st.info("""
        **Netherlands QuizMaster v2.0**
        
        Challenge yourself with engaging quizzes about the Netherlands.
        
        **Features:**
        - 🎯 Multiple categories with varying difficulty
        - 📊 Score tracking with personal stats
        - 🏆 Global leaderboard
        - ⏱️ Timed questions with bonus points
        - 💡 Hints and skip power-ups
        - 🎖️ Achievement system
        - 🤖 AI-generated custom quizzes
        - 💬 Chat with stereotypical Dutch AI
        
        **Tips:**
        - Try higher difficulties for more points
        - Complete a 3-question streak for score multiplier
        - Use hints strategically
        - Check your stats page to track progress
        """)

    # close page container
    st.markdown('</div>', unsafe_allow_html=True)


