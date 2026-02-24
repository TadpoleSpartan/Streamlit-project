import streamlit as st
import json
import random
import time
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Quiz - Netherlands QuizMaster", page_icon="🎮", layout="wide")

# Load custom CSS
ROOT = Path(__file__).parent.parent
CSS_FILE = ROOT / "assets" / "styles.css"
if CSS_FILE.exists():
    st.markdown(f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

DATA_DIR = Path(__file__).parent.parent / "data"
QUESTIONS_FILE = DATA_DIR / "questions.json"
HIGHSCORES_FILE = DATA_DIR / "highscores.json"

def load_questions():
    if QUESTIONS_FILE.exists():
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"categories": {}}

def save_highscore(name, score, category, correct, total):
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
    data["scores"] = sorted(data["scores"], key=lambda x: x["score"], reverse=True)[:50]

    with open(HIGHSCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def init_session_state():
    defaults = {
        "player_name": "",
        "selected_category": None,
        "selected_difficulty": "Medium",
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
        "hints_available": 1,
        "skips_available": 1,
        "time_start": None,
        "total_time": 0,
        "achievements": [],
        "sound_effects": False,
        "last_result": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

def start_game():
    data = load_questions()
    cat = st.session_state.selected_category
    if not cat or cat not in data.get("categories", {}):
        st.error("Please select a valid category on Home or Categories page.")
        return

    questions = data["categories"][cat].copy()
    
    # Filter by difficulty if not "Mixed"
    if st.session_state.selected_difficulty != "Mixed":
        difficulty_map = {"Easy": "easy", "Medium": "medium", "Hard": "hard"}
        target_difficulty = difficulty_map.get(st.session_state.selected_difficulty, "medium")
        questions = [q for q in questions if q.get("difficulty", "medium").lower() == target_difficulty]
        
        # If no questions at that difficulty, use all
        if not questions:
            questions = data["categories"][cat].copy()
    
    random.shuffle(questions)

    st.session_state.questions = questions
    st.session_state.game_active = True
    st.session_state.current_question_index = 0
    st.session_state.score = 0
    st.session_state.correct_answers = 0
    st.session_state.answered_current = False
    st.session_state.selected_answer = None
    st.session_state.show_result = False
    st.session_state.current_streak = 0
    st.session_state.multiplier = 1.0
    st.session_state.hints_available = 1
    st.session_state.skips_available = 1
    st.session_state.time_start = time.time()
    # per-question timer (seconds) - adjust for difficulty
    difficulty_map = {"Easy": 30, "Medium": 25, "Hard": 20}
    st.session_state.time_limit = difficulty_map.get(st.session_state.selected_difficulty, 25)
    st.session_state.time_started_for_question = None

def check_answer(selected_index: int):
    q = st.session_state.questions[st.session_state.current_question_index]
    st.session_state.answered_current = True
    st.session_state.selected_answer = selected_index

    correct = q["correct"]
    base = q.get("points", 10)

    if selected_index == correct:
        st.session_state.last_result = "correct"
        earned = int(base * st.session_state.multiplier)
        st.session_state.score += earned
        st.session_state.correct_answers += 1
        st.session_state.current_streak += 1
        # multiplier rules
        if st.session_state.current_streak >= 3:
            st.session_state.multiplier = 1.5
        elif st.session_state.current_streak == 2:
            st.session_state.multiplier = 1.25
        else:
            st.session_state.multiplier = 1.0
        return True
    else:
        st.session_state.last_result = "wrong"
        st.session_state.current_streak = 0
        st.session_state.multiplier = 1.0
        return False

def next_question():
    # move forward or finish
    if st.session_state.current_question_index < len(st.session_state.questions) - 1:
        st.session_state.current_question_index += 1
        st.session_state.answered_current = False
        st.session_state.selected_answer = None
    else:
        # end game
        st.session_state.total_time = int(time.time() - (st.session_state.time_start or time.time()))
        end_game()

def end_game():
    st.session_state.game_active = False
    st.session_state.show_result = True
    # save highscore
    save_highscore(
        name=st.session_state.player_name or "Anonymous",
        score=st.session_state.score,
        category=st.session_state.selected_category or "Unknown",
        correct=st.session_state.correct_answers,
        total=len(st.session_state.questions)
    )

def show_question():
    questions = st.session_state.questions
    idx = st.session_state.current_question_index
    q = questions[idx]

    # header metrics with custom styling
    st.markdown("""
    <style>
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        gap: 10px;
        margin-bottom: 16px;
    }
    .metric-item {
        background: rgba(31, 111, 235, 0.05);
        border: 1px solid rgba(31, 111, 235, 0.15);
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .metric-value {
        font-size: 18px;
        font-weight: 700;
        color: var(--accent-light);
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 11px;
        color: #6b7684;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        font-weight: 500;
    }
    </style>
    <div class="metrics-grid">
        <div class="metric-item">
            <div class="metric-value">{}</div>
            <div class="metric-label">Score</div>
        </div>
        <div class="metric-item">
            <div class="metric-value">{}</div>
            <div class="metric-label">Correct</div>
        </div>
        <div class="metric-item">
            <div class="metric-value">{:.0f}x</div>
            <div class="metric-label">Boost</div>
        </div>
        <div class="metric-item">
            <div class="metric-value">{}</div>
            <div class="metric-label">Streak</div>
        </div>
    </div>
    """.format(
        st.session_state.score,
        st.session_state.correct_answers,
        st.session_state.multiplier,
        st.session_state.current_streak
    ), unsafe_allow_html=True)

    # Progress bar with percentage
    progress_pct = ((idx+1)/len(questions))*100
    st.markdown(f"""
    <div style='margin-bottom: 20px;'>
        <div style='display: flex; justify-content: space-between; font-size: 12px; color: #6b7684; margin-bottom: 8px; font-weight: 500;'>
            <span>Question {idx+1} of {len(questions)}</span>
            <span>{int(progress_pct)}%</span>
        </div>
        <div style='width: 100%; height: 6px; background: rgba(255,255,255,0.06); border-radius: 999px; overflow: hidden;'>
            <div style='height: 100%; width: {progress_pct}%; background: linear-gradient(90deg, var(--accent), var(--accent-2)); transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);'></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Timer handling
    if st.session_state.time_started_for_question is None:
        st.session_state.time_started_for_question = time.time()

    elapsed = int(time.time() - st.session_state.time_started_for_question)
    remaining = max(0, st.session_state.time_limit - elapsed)
    
    timer_color = "var(--success)" if remaining > 10 else ("var(--warning)" if remaining > 5 else "var(--danger)")
    st.markdown(f"<p style='margin: 0 0 16px 0; font-size: 13px; color: {timer_color}; font-weight: 600;'>⏱ {remaining}s</p>", unsafe_allow_html=True)

    # Auto-timeout handling
    if remaining <= 0 and not st.session_state.answered_current:
        st.warning("⏰ Time's up for this question!")
        # mark as answered wrong
        st.session_state.answered_current = True
        st.session_state.selected_answer = None
        st.session_state.current_streak = 0
        st.session_state.multiplier = 1.0

    # Question display
    difficulty_icons = {'easy': '🟢', 'medium': '🟡', 'hard': '🔴'}
    diff_icon = difficulty_icons.get(q.get('difficulty', 'medium').lower(), '🟡')
    
    st.markdown(f"""
    <div style='background: var(--card); border: 1px solid rgba(255,255,255,0.08); border-radius: 9px; padding: 24px; margin-bottom: 24px;'>
        <h3 style='margin: 0 0 14px 0; font-weight: 500; font-size: 18px; line-height: 1.6; color: white;'>{q['question']}</h3>
        <div style='display: flex; gap: 8px; align-items: center;'>
            <span style='font-size: 11px; color: #6b7684; text-transform: uppercase; font-weight: 600;'>{diff_icon} {q.get("difficulty", "medium").title()}</span>
            <span style='font-size: 11px; color: #6b7684; padding: 2px 8px; background: rgba(255,255,255,0.06); border-radius: 4px; font-weight: 600;'>+{q.get("points", 10)} pts</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Power-ups section
    col_hint, col_skip, col_spacer = st.columns([1, 1, 4])
    with col_hint:
        if st.button(f"💡 Hint", key="hint", use_container_width=True):
            if st.session_state.hints_available > 0 and not st.session_state.answered_current:
                st.session_state.hints_available -= 1
                wrongs = [(i,o) for i,o in enumerate(q['options']) if i != q['correct']]
                if wrongs:
                    i,o = random.choice(wrongs)
                    st.info(f"Not this: '{o}'")
            else:
                st.warning("No hints left")
    with col_skip:
        if st.button(f"⏭️ Skip", key="skip", use_container_width=True):
            if st.session_state.skips_available > 0 and not st.session_state.answered_current:
                st.session_state.skips_available -= 1
                st.session_state.current_streak = 0
                st.session_state.multiplier = 1.0
                st.warning("Question skipped")
                time.sleep(0.6)
                next_question()
                st.rerun()
            else:
                st.warning("No skips left")

    st.markdown("---")

    if not st.session_state.answered_current:
        st.markdown("<p style='margin-bottom: 12px; font-size: 12px; color: #6b7684; text-transform: uppercase; font-weight: 600; letter-spacing: 0.6px;'>Choose answer:</p>", unsafe_allow_html=True)
        
        for i,opt in enumerate(q['options']):
            if st.button(f"{chr(65+i)}. {opt}", key=f"opt_{i}", use_container_width=True):
                correct = check_answer(i)
                st.session_state.time_started_for_question = None
                st.rerun()
    else:
        st.markdown("<p style='margin-bottom: 12px; font-size: 12px; color: #6b7684; text-transform: uppercase; font-weight: 600; letter-spacing: 0.6px;'>Review: (Press Enter to continue)</p>", unsafe_allow_html=True)
        for i,opt in enumerate(q['options']):
            prefix = chr(65+i)
            if i == q['correct']:
                st.markdown(f"<div style='background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 6px; padding: 12px; margin-bottom: 8px;'><strong style='color: #3fb950;'>{prefix}. {opt}</strong> <span style='color: #3fb950; font-size: 12px; font-weight: 600; margin-left: 8px;'>✓ Correct</span></div>", unsafe_allow_html=True)
            elif i == st.session_state.selected_answer:
                st.markdown(f"<div style='background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 12px; margin-bottom: 8px;'><strong style='color: #f85149;'>{prefix}. {opt}</strong> <span style='color: #f85149; font-size: 12px; font-weight: 600; margin-left: 8px;'>✗ Your answer</span></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 12px; margin-bottom: 8px; color: #c9d1d9;'>{prefix}. {opt}</div>", unsafe_allow_html=True)

        if 'explanation' in q:
            st.markdown(f"<div style='border-left: 3px solid var(--accent); background: rgba(31, 111, 235, 0.08); padding: 12px; margin: 16px 0; border-radius: 6px; font-size: 13px; color: #c9d1d9;'><strong style='color: var(--accent-light);'>💡 Explanation:</strong><br>{q['explanation']}</div>", unsafe_allow_html=True)

        if st.button("Next →", key="next_btn", use_container_width=True):
            st.session_state.time_started_for_question = None
            next_question()
            st.rerun()

        # Play sound for last answer if enabled (simple WebAudio tone)
        if st.session_state.get("sound_effects") and st.session_state.get("last_result"):
            tone = '440' if st.session_state.last_result == 'correct' else '220'
            st.markdown(f"""
            <script>
            try {{
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const o = ctx.createOscillator();
                const g = ctx.createGain();
                o.type = 'sine';
                o.frequency.value = {tone};
                o.connect(g);
                g.connect(ctx.destination);
                g.gain.setValueAtTime(0.0001, ctx.currentTime);
                g.gain.exponentialRampToValueAtTime(0.2, ctx.currentTime + 0.01);
                o.start();
                g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.25);
                o.stop(ctx.currentTime + 0.26);
            }} catch(e) {{}}
            </script>
            """, unsafe_allow_html=True)
            # reset last_result to avoid repeating
            st.session_state.last_result = None

def show_results():
    total = len(st.session_state.questions)
    correct = st.session_state.correct_answers
    score = st.session_state.score
    time_taken = st.session_state.total_time
    pct = (correct/total*100) if total>0 else 0
    
    # Determine result tier and achievements
    achievements = []
    if pct >= 90:
        tier = "Perfect"
        emoji = "🎯"
        color = "var(--success)"
        achievements.append("Ace")
    elif pct >= 80:
        tier = "Excellent"
        emoji = "⭐"
        color = "var(--accent-light)"
        achievements.append("Great Score")
    elif pct >= 70:
        tier = "Good"
        emoji = "👍"
        color = "var(--warning)"
    elif pct >= 50:
        tier = "Decent"
        emoji = "📚"
        color = "var(--muted)"
    else:
        tier = "Keep Learning"
        emoji = "🚀"
        color = "var(--danger)"
    
    # Speed achievements
    if time_taken < 60:
        achievements.append("Speed Runner")
    
    # Perfect accuracy achievement
    if pct == 100:
        achievements.append("Perfect Score")
    
    # Streak related
    if st.session_state.current_streak >= 5:
        achievements.append("On Fire")

    st.markdown(f"""
    <div style='text-align: center; padding: 32px 0 24px 0;'>
        <div style='font-size: 56px; margin-bottom: 16px;'>{emoji}</div>
        <h1 style='margin: 0 0 8px 0; font-weight: 600; font-size: 32px; color: white;'>{tier}</h1>
        <p style='margin: 0 0 32px 0; color: #6b7684; font-size: 14px;'>You scored {int(pct)}% correct • {score} points</p>
    </div>
    """, unsafe_allow_html=True)

    # Accuracy visualization
    st.markdown(f"""
    <div style='margin-bottom: 24px;'>
        <p style='margin: 0 0 8px 0; font-size: 12px; color: #6b7684; text-transform: uppercase; font-weight: 600; letter-spacing: 0.6px;'>Accuracy</p>
        <div style='width: 100%; height: 8px; background: rgba(255,255,255,0.06); border-radius: 999px; overflow: hidden;'>
            <div style='height: 100%; width: {pct}%; background: linear-gradient(90deg, var(--accent), var(--accent-2)); transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);'></div>
        </div>
        <p style='margin: 8px 0 0 0; font-size: 13px; color: var(--accent-light); font-weight: 600;'>{correct}/{total} correct • {int(pct)}%</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats in grid
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Points", f"{score:,}")
    with col2:
        st.metric("Accuracy", f"{int(pct)}%")
    with col3:
        st.metric("Time", f"{time_taken}s")
    with col4:
        st.metric("Correct", f"{correct}/{total}")
    
    # Achievements
    if achievements:
        st.markdown("<p style='color: #6b7684; font-size: 12px; margin-top: 20px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px;'>Achievements Unlocked</p>", unsafe_allow_html=True)
        cols = st.columns(len(achievements))
        for idx, achievement in enumerate(achievements):
            with cols[idx]:
                st.markdown(f"""
                <div style='background: rgba(31, 111, 235, 0.1); border: 1px solid rgba(31, 111, 235, 0.2); border-radius: 8px; padding: 12px; text-align: center; animation: slideInRight {0.3 + idx*0.1}s ease;'>
                    <div style='font-size: 20px; margin-bottom: 4px;'>🏆</div>
                    <div style='font-size: 12px; font-weight: 600; color: var(--accent-light);'>{achievement}</div>
                </div>
                """, unsafe_allow_html=True)
    # Share your result (copy to clipboard)
    share_text = f"I scored {score} points ({int(pct)}%) on {st.session_state.get('selected_category','a quiz')} - Netherlands QuizMaster!"
    st.markdown("---")
    st.markdown(f"<div style='display:flex; gap:8px;'>", unsafe_allow_html=True)
    st.markdown(f"<button id='copyScore' style='background: var(--accent); color: white; padding:10px 12px; border-radius:6px; border:none;'>Share Score</button>", unsafe_allow_html=True)
    st.markdown(f"<a href='data:text/plain;charset=utf-8,{share_text}' download='quiz-result.txt' style='background: transparent; border:1px solid rgba(255,255,255,0.08); padding:10px 12px; border-radius:6px; color: #c9d1d9; text-decoration:none;'>Download Summary</a>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    share_text_js = json.dumps(share_text)
    st.markdown(f"""
    <script>
    const text = {share_text_js};
    document.getElementById('copyScore').addEventListener('click', function() {{
        try {{ navigator.clipboard.writeText(text); alert('Copied result to clipboard!'); }} catch(e) {{ prompt('Copy the text below:', text); }}
    }});
    </script>
    """, unsafe_allow_html=True)
    
    if pct >= 90:
        st.balloons()

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("↻ Try Again", key="play_again_btn", use_container_width=True):
            start_game()
            st.rerun()
    with col2:
        if st.button("→ Next Category", key="change_category_btn", use_container_width=True):
            st.session_state.show_result = False
            st.session_state.game_active = False
            st.session_state.selected_category = None
            st.rerun()
    with col3:
        if st.button("⌂ Home", key="home_from_results_btn", use_container_width=True):
            st.session_state.show_result = False
            st.session_state.game_active = False
            st.rerun()

# ============== LOGIN SECTION ==============

def show_login():
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; margin: 40px 0 16px 0; font-weight: 500; font-size: 20px;'>Enter your name</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; margin: 0 0 24px 0; color: #6b7684; font-size: 13px;'>Create or login to track your progress</p>", unsafe_allow_html=True)
        
        login_name = st.text_input("", placeholder="Your name", key="login_input", label_visibility="collapsed")
        
        col_a, col_b = st.columns([1.2, 1])
        with col_a:
            if st.button("Continue", key="login_btn", use_container_width=True):
                if login_name.strip():
                    st.session_state.player_name = login_name.strip()
                    st.rerun()
                else:
                    st.error("Please enter your name")
        with col_b:
            if st.button("Home", key="home_from_login", use_container_width=True):
                st.switch_page("Home.py")

def show_logout():
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"<p style='margin: 0; font-size: 13px; color: #6b7684; text-transform: uppercase; font-weight: 600; letter-spacing: 0.6px;'>👤 {st.session_state.player_name.upper()}</p>", unsafe_allow_html=True)
    with col2:
        if st.button("Logout", key="logout_btn", use_container_width=True):
            st.session_state.player_name = ""
            st.session_state.game_active = False
            st.session_state.show_result = False
            st.rerun()
    with col3:
        if st.button("Home", key="home_btn", use_container_width=True):
            st.switch_page("Home.py")

# ============== MAIN ==============

st.markdown("<h1 style='margin-bottom: 24px; font-weight: 600;'>Quiz</h1>", unsafe_allow_html=True)

if not st.session_state.player_name:
    show_login()
elif st.session_state.show_result:
    show_logout()
    st.markdown("---")
    show_results()
elif not st.session_state.game_active:
    show_logout()
    st.markdown("---")
    
    if st.session_state.selected_category:
        st.markdown(f"<p style='margin-bottom: 12px; color: #6b7684; font-size: 12px; text-transform: uppercase; font-weight: 600; letter-spacing: 0.6px;'>Selected</p>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='margin: 0 0 20px 0; font-weight: 500; font-size: 24px;'>{st.session_state.selected_category}</h2>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if st.button("Begin Quiz", key="start_quiz_btn", use_container_width=True):
                start_game()
                st.rerun()
        with col2:
            if st.button("Change", key="change_cat_btn", use_container_width=True):
                st.switch_page("pages/3_📚_Categories.py")
        with col3:
            st.write("")
    else:
        st.markdown("<p style='text-align: center; color: #6b7684; padding: 60px 20px; font-size: 14px;'>Select a category above to begin</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Browse Categories", key="browse_cat_btn", use_container_width=True):
                st.switch_page("pages/3_📚_Categories.py")
else:
    show_question()
