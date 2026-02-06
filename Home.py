import streamlit as st
import json
from pathlib import Path
import random

# Page configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="Netherlands QuizMaster",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define the path to our data folder
DATA_DIR = Path(__file__).parent / "data"
QUESTIONS_FILE = DATA_DIR / "questions.json"

def load_questions():
    """Load questions from JSON file."""
    if QUESTIONS_FILE.exists():
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"categories": {}}

def get_categories():
    """Get list of available categories."""
    data = load_questions()
    return list(data.get("categories", {}).keys())

# Initialize session state
if "player_name" not in st.session_state:
    st.session_state.player_name = ""
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None
if "streak" not in st.session_state:
  Custom CSS for more fun styling
st.markdown("""
    <style>
    .big-title {
        text-align: center;
        font-size: 3rem;
        color: #FF6B35;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
  Rules Section
with st.expander("📋 Game Rules & How to Play", expanded=False):
    st.markdown("""
    ### 🎮 How to Play:
    1. **Enter Your Name** - Get personalized for your adventure!
    2. **Choose a Category** - Pick from 3 exciting Netherlands topics
    3. **Answer Questions** - Multiple choice questions with 4 options
    4. **Earn Points** - Get more points for harder questions
    5. **Build Your Streak** - Answer correctly to keep the momentum!
    
    ### 🏆 Scoring System:
    - **Easy Questions**: 10 points
    - **Medium Questions**: 15 points
    - **Hard Questions**: 20 points
    - **Bonus**: Get a streak of 3+ correct answers to unlock a multiplier!
    
    ### 🎯 Game Features:
    - 📊 Real-time score tracking
    - 📈 Track your winning streak
    - 🏅 Achievement system
    - 🌟 Instant feedback with animations
    - 🎊 Celebratory balloons for perfect answers!
    """)

# Player name input with fun styling
col1, col2 = st.columns([2, 1])

with col1:
    player_name = st.text_input(
        "🎮 Enter your name to begin your adventure:",
        value=st.session_state.player_name,
        placeholder="Your legendary name here..."
    )
    
    if player_name:
        st.session_state.player_name = player_name

with col2:
    st.write("")  # Spacing
    st.write("")
    if st.session_state.player_name:
        st.success(f"🌟
    .achievement {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        padding: 0.8rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Main page content
st.markdown('<div class="big-title">🎯 Netherlands QuizMaster</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Test Your Knowledge About the Netherlands! 🇳🇱</div>', unsafe_allow_html=True)

# Fun welcome message
fun_greetings = [
    "Welkom! Ready to become a Netherlands expert? 🌷",
    "Hallo! Let's test your Dutch knowledge! 🧀",
    "Goedemorgen! Time to quiz about the Netherlands! 🚲",
    "Hey there! Discover amazing Dutch facts! 🏛️"
]
st.markdown(f"### {random.choice(fun_greetings)}
if "best_streak" not in st.session_state:
    st.session_state.best_streak = 0

# Main page content
st.title("🎯 Netherl with fun descriptions
st.markdown("### 🎓 Choose Your Challenge!")

# Fun category descriptions
category_descriptions = {
    "Netherlands Geography": "🗺️ Explore Dutch cities, borders, and geography!",
    "Dutch Culture & History": "🧀 Discover traditions, food, and historical events!",
    "Famous Dutch People": "⭐ Learn about legendary Dutch artists and explorers!"
}

categories = get_categories()

if categories:
    # Display fun category cards
    cols = st.columns(len(categories))
    
    for idx, (col, category) in enumerate(zip(cols, categories)):
        with col:
            description = category_descriptions.get(category, "")
            if st.button(f"{category}\n\n{description}", use_container_width=True, key=f"cat_{idx}"):
                st.session_state.selected_category = category
    
    st.markdown("---")
    
    # Show selected category info
    if st.session_state.selected_category:
        selected_data = load_questions()
        num_questions = len(selected_data.get("categories", {}).get(st.session_state.selected_category, []))
        
        st.markdown(f"### 📊 {st.session_state.selected_category}")
        st.markdown(f"**Questions:** {num_questions} | **Category selected:** ✅")
    
    st.markdown("---")
    
    # Start quiz button with fun styling
    if st.session_state.player_name:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 LAUNCH THE QUIZ! 🚀", type="primary", use_container_width=True):
                st.success("Buckle up, legend! Get ready for some fun! 🎢")
                st.balloons()
                import time
                time.sleep(1)
                st.switch_page("pages/1_🎮_Quiz.py")
    else:
        st.warning("⚠️ Please enter your legendary name to start the quiz!")
else:
    st.error("No categories found. Please add questions to data/questions.json")

# Fun facts section
st.markdown("---")
st.markdown("### 🇳🇱 Did You Know? Netherlands Fun Facts!")

fun_facts = [
    "🧀 The Netherlands produces over 2 MILLION tons of cheese per year!",
    "🚲 There are more bicycles than people in the Netherlands!",
    "🌷 Tulips were the most expensive flowers in the world during 'Tulip Mania' in the 1600s!",
    "🌊 About 26% of the Netherlands is below sea level, protected by amazing dikes!",
    "🎨 Vincent van Gogh painted over 2,100 artworks in just 37 years!",
    "🧬 The Netherlands has the world's fastest internet speeds!",
    "🏆 Dutch explorer Abel Tasman discovered Tasmania and New Zealand!",
    "🏛️ Amsterdam has more canals than Venice!",
    "📱 The first webcam was created to monitor a coffee pot at Cambridge University by Dutch scientists!",
    "🌍 The Netherlands is the world's 2nd largest exporter of agricultural goods!"
]

st.markdown(f'<div class="fun-fact">{random.choice(fun_facts)}</div>', unsafe_allow_html=True)

# Footer with achievements
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📊 Games Played", st.session_state.total_games)

with col2:
    st.metric("🔥 Current Streak", st.session_state.streak)

with col3:
    st.metric("⭐ Best Streak", st.session_state.best_streak)

st.markdown(
    "<div style='text-align: center; color: gray; margin-top: 2rem;'>"
    "🎓 Made with ❤️ for S6 Informatics | Master the Netherlands! 🇳🇱
if categories:
    selected = st.selectbox(
        "Select category:",
        options=categories,
        index=0 if st.session_state.selected_category is None 
              else categories.index(st.session_state.selected_category)
              if st.session_state.selected_category in categories else 0
    )
    st.session_state.selected_category = selected
    
    # Start quiz button
    if st.session_state.player_name:
        if st.button("🚀 Start Quiz", type="primary", use_container_width=True):
            st.switch_page("pages/1_🎮_Quiz.py")
    else:
        st.warning("Please enter your name to start the quiz.")
else:
    st.error("No categories found. Please add questions to data/questions.json")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Made with ❤️ for S6 Informatics"
    "</div>",
    unsafe_allow_html=True
)
