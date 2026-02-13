import streamlit as st
from pathlib import Path
import json

st.set_page_config(page_title="Settings - Netherlands QuizMaster", page_icon="⚙️")

ROOT = Path(__file__).parent.parent
CSS_FILE = ROOT / "assets" / "styles.css"
if CSS_FILE.exists():
    st.markdown(f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

st.markdown('<h1 style="margin-bottom: 8px; font-weight: 600;">Settings</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #6b7684; margin-bottom: 24px;">Customize your quiz experience</p>', unsafe_allow_html=True)

st.markdown("---")

# Initialize settings in session state if needed
if "sound_effects" not in st.session_state:
    st.session_state.sound_effects = False
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

# Gameplay Settings
st.markdown("### 🎮 Gameplay Settings")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("<p style='margin: 0 0 8px 0; font-size: 14px; color: #c9d1d9;'><strong>Sound Effects</strong></p><p style='margin: 0; font-size: 12px; color: #6b7684;'>Play sounds for correct/incorrect answers</p>", unsafe_allow_html=True)
with col2:
    st.session_state.sound_effects = st.toggle("Sound Effects", value=st.session_state.sound_effects)

st.markdown("---")

# Display Settings
st.markdown("### 🎨 Display Settings")

theme_options = ["Dark", "Light"]
selected_theme = st.selectbox(
    "Theme",
    theme_options,
    index=theme_options.index(st.session_state.theme_mode),
    help="Choose your preferred color theme"
)
st.session_state.theme_mode = selected_theme

st.markdown("---")

# Account Settings
if st.session_state.get("player_name"):
    st.markdown("### 👤 Account Settings")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<p style='margin: 0 0 8px 0; font-size: 14px; color: #c9d1d9;'><strong>Logged in as</strong></p><p style='margin: 0; font-size: 13px; color: var(--accent-light);'>{st.session_state.player_name}</p>", unsafe_allow_html=True)
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.player_name = ""
            st.session_state.selected_category = None
            st.success("Logged out successfully!")
            st.rerun()

    st.markdown("---")
    
    # Statistics Overview
    st.markdown("### 📊 Statistics Overview")
    
    DATA_DIR = ROOT / "data"
    HIGHSCORES_FILE = DATA_DIR / "highscores.json"
    
    if HIGHSCORES_FILE.exists():
        with open(HIGHSCORES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            scores = data.get("scores", [])
    else:
        scores = []
    
    player_scores = [s for s in scores if s.get("name") == st.session_state.player_name]
    
    if player_scores:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Games Played", len(player_scores))
        
        with col2:
            best = max(s.get("score", 0) for s in player_scores)
            st.metric("Best Score", best)
        
        with col3:
            avg = sum(s.get("score", 0) for s in player_scores) / len(player_scores)
            st.metric("Avg Score", f"{avg:.0f}")
        
        with col4:
            total_correct = sum(s.get("correct_answers", 0) for s in player_scores)
            total_questions = sum(s.get("total_questions", 0) for s in player_scores)
            accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
            st.metric("Accuracy", f"{accuracy:.0f}%")

st.markdown("---")

# Help & Info
st.markdown("### ❓ Help & Info")

with st.expander("⭐ Achievements"):
    st.markdown("""
    Unlock achievements by:
    
    - **Ace** - Score 90% or higher on a quiz
    - **Speed Runner** - Complete a quiz in under 60 seconds
    - **Perfect Score** - Get 100% on a quiz
    - **On Fire** - Build a 5-question streak
    """)

with st.expander("⏱️ Difficulty Modes"):
    st.markdown("""
    Each category offers different difficulty levels:
    
    - **🟢 Easy** - 30 seconds per question, standard points
    - **🟡 Medium** - 25 seconds per question, standard points
    - **🔴 Hard** - 20 seconds per question, bonus points
    - **🎲 Mixed** - Random mix of all difficulties
    
    Higher difficulties give more points but less time!
    """)

with st.expander("⚡ Score Multiplier System"):
    st.markdown("""
    Build streaks to increase your score multiplier:
    
    - **1 correct** - 1.0x multiplier (no bonus)
    - **2 correct** - 1.25x multiplier (+25%)
    - **3 correct** - 1.5x multiplier (+50%)
    - **Break streak** - Reset to 1.0x
    
    Answer correctly in a row to maximize your score!
    """)

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    if st.button("⌂ Home", use_container_width=True):
        st.switch_page("Home.py")
with col2:
    if st.button("🏆 Leaderboard", use_container_width=True):
        st.switch_page("pages/2_🏆_Highscores.py")
