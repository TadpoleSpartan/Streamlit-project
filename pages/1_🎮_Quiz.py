import streamlit as st
import json
import random
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Quiz - Netherlands QuizMaster", page_icon="🎮", layout="wide")

# Custom CSS for fun animations
st.markdown("""
    <style>
    .question-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .streak-counter {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin: 0.5rem 0;
    }
    .achievement-popup {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    .combo-meter {
        background-color: #f0f0f0;
        border-radius: 1rem;
        padding: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Constants
DATA_DIR = Path(__file__).parent.parent / "data"
QUESTIONS_FILE = DATA_DIR / "questions.json"
HIGHSCORES_FILE = DATA_DIR / "highscores.json"

# ============== DATA FUNCTIONS ==============

def load_questions():
    """Load all questions from JSON."""
    if QUESTIONS_FILE.exists():
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"categories": {}}

def save_highscore(name, score, category, correct, total):
    """Save a highscore to the JSON file."""
    if HIGHSCORES_FILE.exists():
        with open(HIGHSCORES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"scores": []}
    
    new_entry = {
        "name": name,
        "score": score,
        "category": category,
        "correct_answers": correct,
        "total_questions": total,
        "date": datetime.now().isoformat()
    }
    
    data["scores"].append(new_entry)
    
    # Sort by score (descending) and keep top 10
    data["scores"] = sorted(
        data["scores"], 
        key=lambda x: x["score"], 
        reverse=True
    )[:10]
    
    with open(HIGHSCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# ============== SESSION STATE ==============

def init_session_state():
    defaults = {
        "player_name": "",
        "selected_category": None,
        "game_active": False,
        "current_question_index": 0,
        "score": 0,
        "correct_answers": 0,
        "questions": [],
        "answered_current": False,
        "selected_answer": None,
        "show_result": False,
        "current_streak": 0,
        "multiplier": 1.0,
        "combo_messages": []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============== GAME LOGIC ==============

def start_game():
    """Initialize a new quiz game."""
    data = load_questions()
    category = st.session_state.selected_category
    
    if category and category in data["categories"]:
        questions = data["categories"][category].copy()
        random.shuffle(questions)  # Randomize order
        
        st.session_state.questions = questions
        st.session_state.game_active = True
        st.session_state.current_question_index = 0
        st.session_state.score = 0
        st.session_state.correct_answers = 0
        st.session_state.answered_current = False
        st.session_state.selected_answer = None
        st.session_state.show_result = False

def check_answer(selected_index: int, correct_index: int, points: int):
    """Check if the selected answer is correct."""
    st.session_state.answered_current = True
    st.s# Calculate points with multiplier
        earned_points = int(points * st.session_state.multiplier)
        st.session_state.score += earned_points
        st.session_state.correct_answers += 1
        st.session_state.current_streak += 1
        
        # Update multiplier based on streak
        if st.session_state.current_streak >= 3:
            st.session_state.multiplier = 1.5
        elif st.session_state.current_streak >= 2:
            st.session_state.multiplier = 1.25
        else:
            st.session_state.multiplier = 1.0
            
        return True
    else:
        # Streak broken
        st.session_state.current_streak = 0
        st.session_state.multiplier = 1.0
            st.session_state.score += points
        st.session_state.correct_answers += 1
        return True
    return False

def next_question():
    """Move to the next question or end the game."""
    if st.session_state.current_question_index < len(st.session_state.questions) - 1:
        st.session_state.current_question_index += 1
        st.session_state.answered_current = False
        st.session_state.selected_answer = None
    else:
        end_game()

def end_game():
    """End the quiz and save score."""
    st.session_state.game_active = False
    st.session_state.show_result = True
    
    # Save highscore
    saTop bar with all important stats
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🎯 Score", st.session_state.score)
    with col2:
        st.metric("✅ Correct", st.session_state.correct_answers)
    with col3:
        st.metric("🔥 Streak", st.session_state.current_streak)
    with col4:
        multiplier_text = f"{st.session_state.multiplier}x"
        st.metric("⚡ Multiplier", multiplier_text)
    with col5:
        st.metric("📍 Progress", f"{idx + 1}/{len(questions)}")
    
    # Progress bar
    progress = (idx + 1) / len(questions)
    st.progress(progress)
    
    # Streak celebration messages
    if st.session_state.current_streak == 2:
        st.info("🔥 On fire! Keep it going! 🔥")
    elif st.session_state.current_streak == 3:
        st.success("🔥🔥 TRIPLE COMBO! 25% BONUS ACTIVE! 🔥🔥")
    elif st.session_state.current_streak > 3:
        st.success(f"🔥 MEGA STREAK x{st.session_state.current_streak}! 50% BONUS ACTIVE! 🔥")
    
    st.markdown("---")
    
    # Question in fancy box
    st.markdown(f'<div class="question-box"><h2>{q["question"]}</h2></div>', unsafe_allow_html=True)
    
    difficulty_colors = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
    st.caption(f"{difficulty_colors.get(q['difficulty'], '⚪')} **{q['difficulty'].upper()}** | ⭐ Base: {q['points']} points")
    
    st.markdown("---")
    
    # Answer buttons
    if not st.session_state.answered_current:
        st.markdown("### 📍 Choose Your Answer:")
        
        for i, option in enumerate(q["options"]):
            # Color code for buttons
            button_emoji = ["🅰️", "🅱️", "🅲️", "🅳️"][i]
            
            if st.button(f"{button_emoji} {option}", key=f"opt_{i}", use_container_width=True):
                is_correct = check_answer(i, q["correct"], q["points"])
                st.rerun()
    else:
        # Show results with animations
        st.markdown("### 📊 Results:")
        
        for i, option in enumerate(q["options"]):
            button_emoji = ["🅰️", "🅱️", "🅲️", "🅳️"][i]
            
            if i == q["correct"]:
                st.success(f"{button_emoji} ✓ {option}")
            elif i == st.session_state.selected_answer:
                st.error(f"{button_emoji} ✗ {option}")
            else:
                st.write(f"{button_emoji}  {option}")
        
        st.markdown("---")
        
        # Feedback
        if st.session_state.selected_answer == q["correct"]:
       markdown("# 🏆 QUIZ COMPLETE! 🏆")
    
    total = len(st.session_state.questions)
    correct = st.session_state.correct_answers
    score = st.session_state.score
    
    # Calculate percentage
    percentage = (correct / total) * 100 if total > 0 else 0
    
    # Display metrics in fancy layout
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Final Score", score)
    with col2:
        st.metric("✅ Correct Answers", f"{correct}/{total}")
    with col3:
        st.metric("📊 Accuracy", f"{percentage:.0f}%")
    
    st.markdown("---")
    
    # Grade with celebration
    if percentage >= 95:
        st.markdown('<div class="achievement-popup">🌟 PERFECT SCORE! You are a NETHERLANDS LEGEND! 🌟</div>', unsafe_allow_html=True)
        st.balloons()
    elif percentage >= 90:
        st.markdown('<div class="achievement-popup">🥇 EXCELLENT! You are a NETHERLANDS MASTER! 🥇</div>', unsafe_allow_html=True)
        st.balloons()
    elif percentage >= 80:
        st.success("🥈 GREAT JOB! You know the Netherlands well!")
    elif percentage >= 70:
        st.success("👍 GOOD EFFORT! You're on your way!")
    elif percentage >= 50:
        st.warning("📚 NICE TRY! Keep learning about the Netherlands!")
    else:
        st.info("💪 KEEP PRACTICING! Every quiz makes you smarter!")
    
    st.markdown("---")
    
    # Fun fact based on performance
    st.markdown("### 🇳🇱 Did You Know?")
    performance_facts = {
        "perfect": "The Netherlands has NO mountains - the highest point is only 322 meters!",
        "excellent": "Dutch people are the tallest people in the world!",
        "great": "Amsterdam has 1,281 bridges - more than Venice!",
        "good": "Dutch - Netherlands Championship!")

# Check if player has started properly
if not st.session_state.player_name:
    st.warning("⚠️ Please enter your name on the Home page first.")
    if st.button("Go to Home"):
        st.switch_page("Home.py")

elif st.session_state.show_result:
    show_results()

elif not st.session_state.game_active:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(f"🌟 Welcome, {st.session_state.player_name}!")
        st.write(f"**Category Selected:** {st.session_state.selected_category}")
    
    with col2:
        st.metric("Category", st.session_state.selected_category.split()[0] if st.session_state.selected_category else "")
    
    st.markdown("---")
    
    if st.session_state.selected_category:
        # Fun loading animation
        st.markdown("### 🎮 Ready to compete?")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("✨ Earn points for every correct answer")
        with col2:
            st.info("🔥 Build streaks for bonus multipliers")
        with col3:
            st.info("🏆 Achieve the highest score!")
        
        st.markdown("---")
        
        if st.button("🚀 STARTS QUIZ! 🚀", type="primary", use_container_width=True):
            start_game()
            st.rerun()
    else:
        st.warning("⚠️  = st.columns(3)
    with col1:
        if st.button("🔄 Play Again", use_container_width=True):
            st.session_state.show_result = False
            start_game()
            st.rerun()
    with col2:
        if st.button("🎓 Try Different Category", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key.startswith("game_") or key in ["game_active", "score", "correct_answers", "current_question_index"]:
                    if key in st.session_state:
                        del st.session_state[key]
            st.session_state.show_result = False
            st.switch_page("Home.py")
    with col3:
        if st.button("🏠
def show_results():
    """Display the final results."""
    st.title("🏆 Quiz Complete!")
    
    total = len(st.session_state.questions)
    correct = st.session_state.correct_answers
    score = st.session_state.score
    
    # Calculate percentage
    percentage = (correct / total) * 100 if total > 0 else 0
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Final Score", score)
    with col2:
        st.metric("Correct Answers", f"{correct}/{total}")
    with col3:
        st.metric("Accuracy", f"{percentage:.0f}%")
    
    # Grade
    if percentage >= 90:
        st.success("🌟 Excellent! You're a master!")
    elif percentage >= 70:
        st.success("👍 Great job! Well done!")
    elif percentage >= 50:
        st.warning("📚 Good effort! Keep practicing!")
    else:
        st.info("💪 Don't give up! Try again!")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Play Again", use_container_width=True):
            st.session_state.show_result = False
            start_game()
            st.rerun()
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.show_result = False
            st.switch_page("Home.py")

# ============== MAIN PAGE ==============

st.title("🎮 Quiz Time!")

# Check if player has started properly
if not st.session_state.player_name:
    st.warning("Please enter your name on the Home page first.")
    if st.button("Go to Home"):
        st.switch_page("Home.py")

elif st.session_state.show_result:
    show_results()

elif not st.session_state.game_active:
    st.write(f"Welcome, **{st.session_state.player_name}**!")
    
    if st.session_state.selected_category:
        st.write(f"Category: **{st.session_state.selected_category}**")
        
        if st.button("🚀 Start Quiz", type="primary"):
            start_game()
            st.rerun()
    else:
        st.warning("Please select a category on the Home page.")
        if st.button("Go to Home"):
            st.switch_page("Home.py")

else:
    show_question()
