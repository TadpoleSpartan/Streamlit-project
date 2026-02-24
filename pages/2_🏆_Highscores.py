import streamlit as st
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="Highscores - Netherlands QuizMaster", page_icon="🏆")

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
HIGHSCORES_FILE = DATA_DIR / "highscores.json"


def load_css():
    css_path = ROOT / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def load_highscores():
    if HIGHSCORES_FILE.exists():
        with open(HIGHSCORES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("scores", [])
    return []


load_css()
st.markdown('<h1 style="margin-bottom: 8px; font-weight: 600;">Leaderboard</h1>', unsafe_allow_html=True)

scores = load_highscores()

# Check if user is logged in
if "player_name" not in st.session_state or not st.session_state.player_name:
    st.info("👤 Login on the Home page to track your scores!")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Home", use_container_width=True):
            st.switch_page("Home.py")
else:
    player_name = st.session_state.player_name
    
    # Tabs for global and personal leaderboard
    tab1, tab2 = st.tabs(["Global Leaderboard", "My Stats"])
    
    with tab1:
        st.markdown('<p style="color: #6b7684; margin-bottom: 24px;">Top performers across all categories</p>', unsafe_allow_html=True)
        
        if scores:
            df = pd.DataFrame(scores)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.strftime("%m/%d %H:%M")

            df = df.rename(columns={
                "name": "Player",
                "score": "Score",
                "category": "Category",
                "correct_answers": "Correct",
                "total_questions": "Total",
                "date": "Date"
            })

            df.insert(0, "Rank", range(1, len(df) + 1))
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}
            df["Rank"] = df["Rank"].apply(lambda r: medals.get(r, f"#{r}"))

            st.markdown("---")
            st.markdown("### Top Players")
            top_3 = scores[:3]
            cols = st.columns(3)
            for i, s in enumerate(top_3):
                with cols[i]:
                    medal = medals.get(i+1, "")
                    st.markdown(f"""
                    <div style='background: var(--card); border: 1px solid rgba(255,255,255,0.08); border-radius: 9px; padding: 20px; text-align: center;'>
                        <div style='font-size: 36px; margin-bottom: 12px;'>{medal}</div>
                        <h3 style='margin: 0 0 8px 0; font-weight: 600; font-size: 16px;'>{s['name']}</h3>
                        <p style='margin: 0 0 4px 0; color: var(--accent-light); font-size: 20px; font-weight: 700;'>{s['score']} pts</p>
                        <p style='margin: 0; color: #6b7684; font-size: 12px;'>{s['category']}</p>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### All Scores")
            st.dataframe(df, use_container_width=True, hide_index=True)
            # Export options for admins / download
            try:
                csv_all = df.drop(columns=[c for c in df.columns if c == 'Rank']).to_csv(index=False).encode('utf-8')
                st.download_button("Download All Scores (CSV)", data=csv_all, file_name="all_scores.csv", mime="text/csv")
                st.download_button("Download All Scores (JSON)", data=json.dumps(scores, indent=2), file_name="all_scores.json", mime="application/json")
            except Exception:
                pass

            st.markdown("---")
            st.markdown("### Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Games", len(scores))
            with col2:
                avg_score = sum(s["score"] for s in scores) / len(scores)
                st.metric("Avg Score", f"{avg_score:.0f}")
            with col3:
                top_score = max(s["score"] for s in scores)
                st.metric("Best Score", top_score)
            with col4:
                avg_accuracy = (sum(s["correct_answers"] for s in scores) / sum(s["total_questions"] for s in scores) * 100) if scores else 0
                st.metric("Avg Accuracy", f"{avg_accuracy:.0f}%")
        else:
            st.markdown("""
            <div style='background: var(--card); border: 1px solid rgba(255,255,255,0.08); border-radius: 9px; padding: 40px; text-align: center;'>
                <div style='font-size: 36px; margin-bottom: 16px;'>🎮</div>
                <h3 style='margin: 0 0 8px 0; font-weight: 600;'>No scores yet</h3>
                <p style='margin: 0; color: #6b7684; font-size: 14px;'>Play a quiz to see your score on the leaderboard</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Start Quiz", key="play_now_btn", use_container_width=True):
                st.switch_page("Home.py")
    
    with tab2:
        st.markdown(f'<p style="color: #6b7684; margin-bottom: 24px;">Your personal quiz statistics</p>', unsafe_allow_html=True)
        
        # Filter scores for this player
        player_scores = [s for s in scores if s.get("name") == player_name]
        
        if player_scores:
            # Personal stats header
            st.markdown("---")
            st.markdown("### Your Best Performances")
            
            # Sort by score descending
            sorted_scores = sorted(player_scores, key=lambda x: x.get("score", 0), reverse=True)
            top_personal = sorted_scores[:3]
            
            cols = st.columns(3)
            for i, s in enumerate(top_personal):
                with cols[i]:
                    medal = medals.get(i+1, "⭐") if i < 3 else "⭐"
                    st.markdown(f"""
                    <div style='background: var(--card); border: 1px solid rgba(255,255,255,0.08); border-radius: 9px; padding: 20px; text-align: center;'>
                        <div style='font-size: 36px; margin-bottom: 12px;'>{medal}</div>
                        <h3 style='margin: 0 0 8px 0; font-weight: 600; font-size: 16px;'>{s['category']}</h3>
                        <p style='margin: 0 0 4px 0; color: var(--accent-light); font-size: 20px; font-weight: 700;'>{s['score']} pts</p>
                        <p style='margin: 0; color: #6b7684; font-size: 12px;'>{s['correct_answers']}/{s['total_questions']} correct</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Personal statistics
            st.markdown("---")
            st.markdown("### Your Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Games Played", len(player_scores))
            with col2:
                avg_score = sum(s.get("score", 0) for s in player_scores) / len(player_scores)
                st.metric("Avg Score", f"{avg_score:.0f}")
            with col3:
                best_score = max(s.get("score", 0) for s in player_scores)
                st.metric("Personal Best", best_score)
            with col4:
                total_correct = sum(s.get("correct_answers", 0) for s in player_scores)
                total_questions = sum(s.get("total_questions", 0) for s in player_scores)
                accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
                st.metric("Accuracy", f"{accuracy:.0f}%")

            # Charts and export for personal history
            st.markdown("---")
            st.markdown("### Performance Over Time")
            player_df = pd.DataFrame(player_scores)
            if not player_df.empty:
                if "date" in player_df.columns:
                    player_df["date"] = pd.to_datetime(player_df["date"]) 
                    player_df = player_df.sort_values("date")
                else:
                    player_df["date"] = range(len(player_df))

                # Line chart for scores over time
                try:
                    fig = px.line(player_df, x="date", y="score", markers=True, title="Score Over Time")
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    st.line_chart(player_df["score"])

                # Category distribution
                try:
                    fig2 = px.pie(player_df, names="category", title="Category Distribution")
                    st.plotly_chart(fig2, use_container_width=True)
                except Exception:
                    pass

                # Export CSV
                csv_bytes = player_df.to_csv(index=False).encode("utf-8")
                st.download_button("Download My Scores (CSV)", data=csv_bytes, file_name="my_scores.csv", mime="text/csv")
            
            # Scores by category
            st.markdown("---")
            st.markdown("### Scores by Category")
            
            from collections import defaultdict
            category_stats = defaultdict(list)
            for s in player_scores:
                category_stats[s.get("category", "Unknown")].append(s)
            
            for category in sorted(category_stats.keys()):
                cat_scores = category_stats[category]
                best_cat_score = max(s.get("score", 0) for s in cat_scores)
                avg_cat_score = sum(s.get("score", 0) for s in cat_scores) / len(cat_scores)
                
                st.markdown(f"""
                <div style='background: var(--card); border: 1px solid rgba(255,255,255,0.08); border-radius: 9px; padding: 16px; margin-bottom: 12px;'>
                    <h4 style='margin: 0 0 12px 0; font-weight: 600; font-size: 14px;'>{category}</h4>
                    <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; font-size: 12px;'>
                        <div><span style='color: #6b7684;'>Attempts:</span> <strong>{len(cat_scores)}</strong></div>
                        <div><span style='color: #6b7684;'>Best:</span> <strong style='color: var(--accent-light);'>{best_cat_score} pts</strong></div>
                        <div><span style='color: #6b7684;'>Average:</span> <strong>{avg_cat_score:.0f} pts</strong></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background: var(--card); border: 1px solid rgba(255,255,255,0.08); border-radius: 9px; padding: 40px; text-align: center;'>
                <div style='font-size: 36px; margin-bottom: 16px;'>📊</div>
                <h3 style='margin: 0 0 8px 0; font-weight: 600;'>No scores yet</h3>
                <p style='margin: 0; color: #6b7684; font-size: 14px;'>Start a quiz to build your statistics</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Start Quiz", key="play_now_btn_2", use_container_width=True):
                st.switch_page("pages/1_🎮_Quiz.py")

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("⌂ Home", use_container_width=True):
        st.switch_page("Home.py")
with col2:
    if st.button("📚 Categories", use_container_width=True):
        st.switch_page("pages/3_📚_Categories.py")
