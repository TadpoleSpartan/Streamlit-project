import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Categories - Netherlands QuizMaster", page_icon="📚", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .category-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .stat-badge {
        background-color: rgba(255, 255, 255, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        display: inline-block;
        margin: 0.3rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("# 📚 Quiz Categories")
st.markdown("### 🇳🇱 Choose Your Netherlands Challenge!")

DATA_DIR = Path(__file__).parent.parent / "data"
QUESTIONS_FILE = DATA_DIR / "questions.json"

def load_questions():
    if QUESTIONS_FILE.exists():
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"categories": {}}

data = load_questions()
categories = data.get("categories", {})

# Category descriptions and emojis
category_info = {
    "Netherlands Geography": {
        "emoji": "🗺️",
        "description": "Explore the Dutch landscape, cities, and geography!",
        "fun_fact": "The Netherlands has NO natural mountains! 🏔️"
    },
    "Dutch Culture & History": {
        "emoji": "🧀",
        "description": "Discover Dutch traditions, delicious foods, and fascinating history!",
        "fun_fact": "There are MORE bicycles than people in the Netherlands! 🚲"
    },
    "Famous Dutch People": {
        "emoji": "⭐",
        "description": "Learn about legendary Dutch artists, explorers, and pioneers!",
        "fun_fact": "Dutch people are the tallest in the world! 📏"
    }
}

if categories:
    # Display each category as an attractive card
    for name, questions_list in categories.items():
        info = category_info.get(name, {"emoji": "❓", "description": name, "fun_fact": ""})
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Count by difficulty
            difficulties = {}
            total_points = 0
            
            for q in questions_list:
                diff = q.get("difficulty", "unknown")
                difficulties[diff] = difficulties.get(diff, 0) + 1
                total_points += q.get("points", 0)
            
            # Display stats with visual badges
            st.markdown(f"""
            <div class="category-card">
                <h2>{info['emoji']} {name}</h2>
                <p>{info['description']}</p>
                <div style='margin: 1rem 0;'>
                    <span class='stat-badge'>📝 {len(questions_list)} Questions</span>
                    <span class='stat-badge'>⭐ {total_points} Points</span>
                </div>
                <div style='margin: 1rem 0;'>
                    <span class='stat-badge'>🟢 Easy: {difficulties.get('easy', 0)}</span>
                    <span class='stat-badge'>🟡 Med: {difficulties.get('medium', 0)}</span>
                    <span class='stat-badge'>🔴 Hard: {difficulties.get('hard', 0)}</span>
                </div>
                <p style='margin-top: 1rem; font-style: italic;'>💡 {info['fun_fact']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("📋 Sample Questions:")
            
            for idx, q in enumerate(questions_list[:5], 1):
                difficulty_emoji = {
                    "easy": "🟢",
                    "medium": "🟡",
                    "hard": "🔴"
                }.get(q.get("difficulty", "unknown"), "⚪")
                
                st.write(f"{idx}. {difficulty_emoji} {q['question']}")
            
            if len(questions_list) > 5:
                st.caption(f"... and {len(questions_list) - 5} more exciting questions!")
            
            st.markdown("---")
            
            # Quick play buttons
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button(f"🚀 Play {name}", key=f"play_{name}", use_container_width=True):
                    if not st.session_state.get("player_name"):
                        st.warning("Please enter your name on the Home page first!")
                    else:
                        st.session_state.selected_category = name
                        st.switch_page("pages/1_🎮_Quiz.py")
            
            with col_b:
                if st.button(f"📊 View Details", key=f"details_{name}", use_container_width=True):
                    st.session_state.selected_category = name
        
        st.markdown("---")

else:
    st.warning("🚨 No categories found!")
    st.info("Please add questions to data/questions.json")

# Fun separator
st.markdown("### 🌟 Choose a category and start your Netherlands adventure!")

col1, col2 = st.columns(2)
with col1:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("Home.py")
with col2:
    if st.button("🏆 View Leaderboard", use_container_width=True):
        st.switch_page("pages/2_🏆_Highscores.py")
