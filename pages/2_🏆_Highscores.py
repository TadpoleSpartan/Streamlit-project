import streamlit as st
import json
from pathlib import Path
import pandas as pd

st.set_page_config(page_title="Highscores - Netherlands QuizMaster", page_icon="🏆")

# Custom CSS
st.markdown("""
    <style>
    .trophy-header {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .fun-stat {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="trophy-header">🏆 HALL OF FAME 🏆</div>', unsafe_allow_html=True)
st.markdown("### 🇳🇱 Netherlands Quiz Champions!")

DATA_DIR = Path(__file__).parent.parent / "data"
HIGHSCORES_FILE = DATA_DIR / "highscores.json"

def load_highscores():
    """Load highscores from JSON file."""
    if HIGHSCORES_FILE.exists():
        with open(HIGHSCORES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("scores", [])
    return []

scores = load_highscores()

if scores:
    # Convert to DataFrame for nice display
    df = pd.DataFrame(scores)
    
    # Format the date column
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d %H:%M")
    
    # Rename columns for display
    df = df.rename(columns={
        "name": "Player",
        "score": "Score",
        "category": "Category",
        "correct_answers": "Correct",
        "total_questions": "Total",
        "date": "Date"
    })
    
    # Add rank column
    df.insert(0, "Rank", range(1, len(df) + 1))
    
    # Display with medals for top 3
    def add_medal(rank):
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        return medals.get(rank, f"#{rank}")
    
    df["Rank"] = df["Rank"].apply(add_medal)
    
    # Show top 3 in special way
    st.markdown("---")
    st.subheader("🌟 Top 3 Champions!")
    
    top_3_cols = st.columns(3)
    for idx in range(min(3, len(scores))):
        score = scores[idx]
        medals = {0: "🥇", 1: "🥈", 2: "🥉"}
        
        with top_3_cols[idx]:
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #FFD700, #FFA500);
                padding: 1.5rem;
                border-radius: 1rem;
                text-align: center;
                color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            '>
                <h2>{medals[idx]}</h2>
                <h3>{score['name']}</h3>
                <p style='font-size: 1.5rem; font-weight: bold;'>⭐ {score['score']} points</p>
                <p>{score['category']}</p>
                <p style='font-size: 0.9rem;'>✅ {score['correct_answers']}/{score['total_questions']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📊 Full Leaderboard")
    
    # Display as table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # Statistics
    st.markdown("---")
    st.subheader("📈 Netherlands Quiz Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'''
        <div class="fun-stat">
        📊<br>Total Games<br><h2>{len(scores)}</h2>
        </div>
        ''', unsafe_allow_html=True)
    with col2:
        avg_score = sum(s["score"] for s in scores) / len(scores)
        st.markdown(f'''
        <div class="fun-stat">
        📈<br>Average Score<br><h2>{avg_score:.0f}</h2>
        </div>
        ''', unsafe_allow_html=True)
    with col3:
        top_score = max(s["score"] for s in scores)
        st.markdown(f'''
        <div class="fun-stat">
        ⭐<br>Highest Score<br><h2>{top_score}</h2>
        </div>
        ''', unsafe_allow_html=True)
    with col4:
        avg_accuracy = (sum(s["correct_answers"] for s in scores) / sum(s["total_questions"] for s in scores) * 100) if scores else 0
        st.markdown(f'''
        <div class="fun-stat">
        ✅<br>Avg Accuracy<br><h2>{avg_accuracy:.0f}%</h2>
        </div>
        ''', unsafe_allow_html=True)

else:
    st.markdown('<div class="trophy-header">🎮 Be the First Legend! 🎮</div>', unsafe_allow_html=True)
    st.markdown("### No champions yet! Your score could be here!")
    st.info("📌 Play a quiz and you'll appear on this leaderboard!")
    
    if st.button("🎮 Play Now and Make History!", key="play_now"):
        st.switch_page("Home.py")

st.markdown("---")
if st.button("🏠 Back to Home", use_container_width=True):
    st.switch_page("Home.py")
