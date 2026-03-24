import streamlit as st
import json
import random
import time
from pathlib import Path
from datetime import datetime
import openai

from json_utils import safe_load_json, safe_save_json, ensure_json_file

st.set_page_config(page_title="Quiz - Netherlands QuizMaster", page_icon="🎮", layout="wide")

# Load custom CSS
ROOT = Path(__file__).parent.parent
CSS_FILE = ROOT / "assets" / "styles.css"
if CSS_FILE.exists():
    st.markdown(f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# Page container for consistent layout
st.markdown('<div class="container">', unsafe_allow_html=True)

DATA_DIR = Path(__file__).parent.parent / "data"
QUESTIONS_FILE = DATA_DIR / "questions.json"
HIGHSCORES_FILE = DATA_DIR / "highscores.json"

# ensure files exist on every page load
DATA_DIR.mkdir(parents=True, exist_ok=True)
ensure_json_file(QUESTIONS_FILE, {"categories": {}})
ensure_json_file(HIGHSCORES_FILE, {"scores": []})

def load_questions():
    """Load questions from the JSON file safely."""
    # always read fresh using utility; handle invalid file gracefully
    return safe_load_json(QUESTIONS_FILE, {"categories": {}})


def generate_questions_with_ai(category, num_questions=5, difficulty="medium"):
    """Generate quiz questions using OpenAI."""
    try:
        client = openai.OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
        prompt = f"Generate {num_questions} multiple-choice questions about {category}. Each question should have 4 options, with one correct answer. Difficulty: {difficulty}. Write the questions, options, and explanations in English, but make them very stereotypical Dutch: use words like 'lekker', 'gezellig', 'goed zo', references to cheese, bikes, windmills, tulips, coffee, being direct/blunt, thrifty, weather complaints, flat landscapes, and other classic Dutch stereotypes. Infuse with Dutch humor and cultural quirks as if written by a stereotypical Dutch person speaking English. Format as JSON array of objects with keys: 'question', 'options' (array of 4 strings), 'correct' (index 0-3), 'difficulty', 'points' (10 for easy, 15 medium, 20 hard), 'explanation' (brief explanation)."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        questions = json.loads(content)
        return questions
    except Exception as e:
        st.error(f"Failed to generate questions: {e}")
        return []


def check_for_updates():
    """Check if the questions file has been updated and notify if necessary."""
    try:
        mtime = QUESTIONS_FILE.stat().st_mtime
    except Exception:
        mtime = None
    prev = st.session_state.get("questions_mtime")
    if mtime and mtime != prev:
        st.session_state.questions_mtime = mtime
        st.session_state.questions_updated = True
        if st.session_state.get("game_active"):
            st.info("Questions file changed; new questions will be used after this game finishes.")
        else:
            st.info("Question database updated, changes will apply next time you start a game.")

# trigger update check whenever page is rendered (moved below after session init)


def save_highscore(name, score, category, correct, total):
    # load existing data safely
    data = safe_load_json(HIGHSCORES_FILE, {"scores": []})

    pct = (correct / total * 100) if total > 0 else 0
    level = st.session_state.get("level", 1)

    # derive a title for the player at the end of the quiz
    if pct >= 90 and level >= 10:
        title = "Dutch Master"
    elif pct >= 90:
        title = "Golden Tulip"
    elif pct >= 80:
        title = "Windmill Wielder"
    elif pct >= 70:
        title = "Canal Cruiser"
    elif pct >= 50:
        title = "Apprentice"
    else:
        title = "Tulip Trainee"

    new_entry = {
        "name": name,
        "score": score,
        "category": category,
        "correct_answers": correct,
        "total_questions": total,
        "date": datetime.now().isoformat(),
        "achievements": st.session_state.get("achievements", []),
        "difficulty": st.session_state.get("selected_difficulty", "Medium"),
        "level": level,
        "title": title
    }

    data.setdefault("scores", []).append(new_entry)
    data["scores"] = sorted(data["scores"], key=lambda x: x.get("score", 0), reverse=True)[:50]

    if not safe_save_json(HIGHSCORES_FILE, data):
        st.error("Failed to persist highscore.")

def init_session_state():
    defaults = {
        "player_name": "",
        "selected_category": None,
        "selected_difficulty": "Medium",
        "level": 1,
        "max_level": 20,
        "level_mode": True,
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
        "fifty_fifty_available": 1,
        "hidden_options": [],
        "time_start": None,
        "total_time": 0,
        "achievements": [],
        "sound_effects": False,
        "last_result": None,
        "confetti_done": False,
        "tick_sound_active": False,
        "times_up_sound_played": False,
        "ai_generated_questions": []
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# now that session defaults exist, check for file updates
check_for_updates()

def start_game():
    # beginning of a fresh game; clear any pending update notification
    if st.session_state.get("questions_updated"):
        st.session_state.questions_updated = False
    data = load_questions()
    cat = st.session_state.selected_category
    if cat and cat.startswith("AI: "):
        # Use AI generated questions
        questions_all = st.session_state.get("ai_generated_questions", [])
        if not questions_all:
            st.error("No AI questions available. Please generate them first.")
            return
        st.session_state.level_mode = False  # Disable level mode for AI quizzes
    elif not cat or cat not in data.get("categories", {}):
        st.error("Please select a valid category on Home or Categories page.")
        return
    else:
        questions_all = data["categories"][cat].copy()
    level = st.session_state.get("level", 1)
    max_level = st.session_state.get("max_level", 20)

    if st.session_state.get("level_mode", True):
        # Define level -> allowed difficulties and question counts
        level_cfg = {
            1: {"difficulties": ["easy"], "num_q": 5},
            2: {"difficulties": ["easy", "medium"], "num_q": 6},
            3: {"difficulties": ["medium"], "num_q": 7},
            4: {"difficulties": ["medium", "hard"], "num_q": 8},
            5: {"difficulties": ["hard"], "num_q": 10},
            6: {"difficulties": ["hard"], "num_q": 12},
            7: {"difficulties": ["hard"], "num_q": 15},
            8: {"difficulties": ["hard"], "num_q": 18},
            9: {"difficulties": ["hard"], "num_q": 20},
            10: {"difficulties": ["hard"], "num_q": 25},
            11: {"difficulties": ["hard"], "num_q": 30},
            12: {"difficulties": ["hard"], "num_q": 35},
            13: {"difficulties": ["hard"], "num_q": 40},
            14: {"difficulties": ["hard"], "num_q": 45},
            15: {"difficulties": ["hard"], "num_q": 50},
            16: {"difficulties": ["hard"], "num_q": 55},
            17: {"difficulties": ["hard"], "num_q": 60},
            18: {"difficulties": ["hard"], "num_q": 65},
            19: {"difficulties": ["hard"], "num_q": 70},
            20: {"difficulties": ["hard"], "num_q": 75}
        }
        cfg = level_cfg.get(min(level, 20), level_cfg[20])
        allowed = cfg.get("difficulties", ["hard"]) 
        # filter by allowed difficulties
        questions = [q for q in questions_all if q.get("difficulty", "medium").lower() in allowed]
        if not questions:
            questions = questions_all.copy()
        # limit number of questions for this level
        if cfg.get("num_q"):
            questions = questions[: cfg["num_q"]]
    else:
        questions = questions_all.copy()
        # Filter by difficulty if not "Mixed"
        if st.session_state.selected_difficulty != "Mixed":
            difficulty_map = {"Easy": "easy", "Medium": "medium", "Hard": "hard"}
            target_difficulty = difficulty_map.get(st.session_state.selected_difficulty, "medium")
            questions = [q for q in questions if q.get("difficulty", "medium").lower() == target_difficulty]
            if not questions:
                questions = questions_all.copy()

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
    st.session_state.fifty_fifty_available = 1
    st.session_state.hidden_options = []
    st.session_state.time_start = time.time()
    # per-question timer (seconds) - adjust for difficulty
    difficulty_map = {"Easy": 30, "Medium": 25, "Hard": 20}
    st.session_state.time_limit = difficulty_map.get(st.session_state.selected_difficulty, 25)
    st.session_state.time_started_for_question = None
    st.session_state.tick_sound_active = False
    st.session_state.times_up_sound_played = False

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
        # allow confetti + sound on correct answers
        st.session_state.confetti_done = False
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
        st.session_state.confetti_done = False
        st.session_state.tick_sound_active = False
        st.session_state.times_up_sound_played = False
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

    if not questions or len(questions) == 0:
        st.error("No questions available for this category and difficulty. Please select a different category or difficulty.")
        st.markdown("<p style='font-size:14px; color:#c9d1d9;'>Go to <strong>Categories</strong> and pick a different set, or check the Editor to add more questions.</p>", unsafe_allow_html=True)
        if st.button("Go to Categories", use_container_width=True):
            st.experimental_set_query_params(page="3_📚_Categories")
        return

    # Show current level when level progression is active
    if st.session_state.get("level_mode", False):
        lvl = st.session_state.get("level", 1)
        st.markdown(f"<div style='margin-bottom:8px;'><span class='badge'>Level {lvl}</span></div>", unsafe_allow_html=True)

    # header metrics with custom styling
    st.markdown(f"""
    <style>
    .metrics-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        gap: 10px;
        margin-bottom: 16px;
    }}
    .metric-item {{
        background: rgba(31, 111, 235, 0.05);
        border: 1px solid rgba(31, 111, 235, 0.15);
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }}
    .metric-value {{
        font-size: 18px;
        font-weight: 700;
        color: var(--accent-light);
        margin-bottom: 4px;
    }}
    .metric-label {{
        font-size: 11px;
        color: #6b7684;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        font-weight: 500;
    }}
    </style>
    <div class="metrics-grid">
        <div class="metric-item">
            <div class="metric-value">{st.session_state.score}</div>
            <div class="metric-label">Score</div>
        </div>
        <div class="metric-item">
            <div class="metric-value">{st.session_state.correct_answers}</div>
            <div class="metric-label">Correct</div>
        </div>
        <div class="metric-item">
            <div class="metric-value">{st.session_state.multiplier:.0f}x</div>
            <div class="metric-label">Boost</div>
        </div>
        <div class="metric-item">
            <div class="metric-value">{st.session_state.current_streak}</div>
            <div class="metric-label">Streak</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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

    # Tick + times-up sound effects (if enabled)
    if st.session_state.get("sound_effects"):
        tick_script = """
        <script>
        (function() {{
            try {{
                if (!window.quizAudioCtx) {{
                    window.quizAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
                }}
                const ctx = window.quizAudioCtx;
                const playTone = (freq, duration) => {{
                    const o = ctx.createOscillator();
                    const g = ctx.createGain();
                    o.connect(g);
                    g.connect(ctx.destination);
                    o.frequency.value = freq;
                    g.gain.setValueAtTime(0.0001, ctx.currentTime);
                    o.start();
                    g.gain.exponentialRampToValueAtTime(0.2, ctx.currentTime + 0.01);
                    g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);
                    o.stop(ctx.currentTime + duration + 0.02);
                }};

                const remaining = {remaining};
                const answered = {answered};
                const timesUpPlayed = window.quizTimesUpPlayed === true;

                if (window.quizTickInterval) {{
                    clearInterval(window.quizTickInterval);
                    window.quizTickInterval = null;
                }}

                if (!answered && remaining > 0) {{
                    window.quizTickInterval = setInterval(() => playTone(880, 0.06), 1000);
                    window.quizTimesUpPlayed = false;
                    setTimeout(() => {{
                        if (window.quizTickInterval) {{
                            clearInterval(window.quizTickInterval);
                            window.quizTickInterval = null;
                        }}
                        if (!window.quizTimesUpPlayed) {{
                            playTone(220, 0.5);
                            window.quizTimesUpPlayed = true;
                        }}
                    }}, remaining * 1000);
                }} else {{
                    if (remaining <= 0 && !timesUpPlayed) {{
                        playTone(220, 0.5);
                        window.quizTimesUpPlayed = true;
                    }}
                }}
            }} catch (e) {{
                // audio may be blocked or unsupported
            }}
        }})();
        </script>
        """.format(
            remaining=remaining,
            answered=str(st.session_state.answered_current).lower()
        )

        st.markdown(tick_script, unsafe_allow_html=True)

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
    
    question_text = q.get('question', '').strip() or "(No question text; check your question file)"
    st.markdown(f"""
    <div style='background: white; border: 1px solid rgba(255,255,255,0.08); border-radius: 9px; padding: 24px; margin-bottom: 24px;'>
        <h3 style='margin: 0 0 14px 0; font-weight: 500; font-size: 18px; line-height: 1.6; color: black;'>{question_text}</h3>
        <div style='display: flex; gap: 8px; align-items: center;'>
            <span style='font-size: 11px; color: #6b7684; text-transform: uppercase; font-weight: 600;'>{diff_icon} {q.get("difficulty", "medium").title()}</span>
            <span style='font-size: 11px; color: #6b7684; padding: 2px 8px; background: rgba(255,255,255,0.06); border-radius: 4px; font-weight: 600;'>+{q.get("points", 10)} pts</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Power-ups section
    col_hint, col_skip, col_fifty, col_spacer = st.columns([1, 1, 1, 3])
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
    with col_fifty:
        if st.button(f"50/50", key="fifty", use_container_width=True):
            if st.session_state.fifty_fifty_available > 0 and not st.session_state.answered_current:
                st.session_state.fifty_fifty_available -= 1
                wrongs = [i for i,o in enumerate(q['options']) if i != q['correct']]
                if len(wrongs) >= 2:
                    to_remove = random.sample(wrongs, 2)
                    st.session_state.hidden_options = to_remove
                    st.info("Two wrong answers removed!")
                else:
                    st.warning("Not enough options to remove")
            else:
                st.warning("No 50/50 left")

    st.markdown("---")

    if not st.session_state.answered_current:
        st.markdown("<p style='margin-bottom: 12px; font-size: 12px; color: #6b7684; text-transform: uppercase; font-weight: 600; letter-spacing: 0.6px;'>Choose answer:</p>", unsafe_allow_html=True)
        
        for i,opt in enumerate(q['options']):
            if i not in st.session_state.hidden_options:
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
            # show confetti on correct answers once
            if st.session_state.get("last_result") == "correct" and not st.session_state.get("confetti_done", False):
                st.session_state.confetti_done = True
                st.markdown(
                    """
                    <script>
                    // simple confetti adapted for Streamlit
                    (() => {
                      const colors = ['#ae1c28', '#ffb700', '#21468b', '#ffffff'];
                      const duration = 1200;
                      const end = Date.now() + duration;
                      const canvas = document.createElement('canvas');
                      canvas.style.position = 'fixed';
                      canvas.style.top = 0;
                      canvas.style.left = 0;
                      canvas.style.width = '100%';
                      canvas.style.height = '100%';
                      canvas.style.pointerEvents = 'none';
                      canvas.style.zIndex = 9999;
                      document.body.appendChild(canvas);
                      const ctx = canvas.getContext('2d');
                      const particles = [];
                      const rand = (min, max) => Math.random() * (max - min) + min;

                      function resize() {
                        canvas.width = window.innerWidth;
                        canvas.height = window.innerHeight;
                      }
                      resize();
                      window.addEventListener('resize', resize);

                      function draw() {
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        const now = Date.now();
                        if (now > end) {
                          window.removeEventListener('resize', resize);
                          document.body.removeChild(canvas);
                          return;
                        }

                        particles.forEach(p => {
                          p.x += p.vx;
                          p.y += p.vy;
                          p.vy += 0.15;
                          p.rotation += p.vr;
                          ctx.save();
                          ctx.translate(p.x, p.y);
                          ctx.rotate(p.rotation);
                          ctx.fillStyle = p.color;
                          ctx.fillRect(-p.size/2, -p.size/2, p.size, p.size);
                          ctx.restore();
                        });
                        requestAnimationFrame(draw);
                      }

                      for (let i = 0; i < 180; i++) {
                        particles.push({
                          x: window.innerWidth / 2,
                          y: window.innerHeight / 2,
                          vx: rand(-8, 8),
                          vy: rand(-12, -2),
                          vr: rand(-0.15, 0.15),
                          rotation: rand(0, Math.PI * 2),
                          size: rand(6, 12),
                          color: colors[Math.floor(rand(0, colors.length))]
                        });
                      }

                      draw();
                    })();
                    </script>
                    """,
                    unsafe_allow_html=True,
                )
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

    # Title (badge) based on performance and level
    if pct >= 90 and st.session_state.get("level", 1) >= 10:
        title = "Dutch Master"
    elif pct >= 90:
        title = "Golden Tulip"
    elif pct >= 80:
        title = "Windmill Wielder"
    elif pct >= 70:
        title = "Canal Cruiser"
    elif pct >= 50:
        title = "Apprentice"
    else:
        title = "Tulip Trainee"
    
    # Speed achievements
    if time_taken < 60:
        achievements.append("Speed Runner")
    
    # Perfect accuracy achievement
    if pct == 100:
        achievements.append("Perfect Score")
    
    # Streak related
    if st.session_state.current_streak >= 5:
        achievements.append("On Fire")
    
    # Power-up related
    if st.session_state.hints_available == 0 and st.session_state.skips_available == 0 and st.session_state.fifty_fifty_available == 0:
        achievements.append("Power User")
    
    if st.session_state.hints_available == 1 and st.session_state.skips_available == 1 and st.session_state.fifty_fifty_available == 1:
        achievements.append("Natural Talent")

    st.markdown(f"""
    <div style='text-align: center; padding: 32px 0 24px 0;'>
        <div style='font-size: 56px; margin-bottom: 16px;'>{emoji}</div>
        <h1 style='margin: 0 0 8px 0; font-weight: 600; font-size: 32px; color: white;'>{tier}</h1>
        <p style='margin: 0 0 8px 0; color: #6b7684; font-size: 14px;'>You scored {int(pct)}% correct • {score} points</p>
        <p style='margin: 0 0 32px 0; font-size: 14px; color: var(--accent); font-weight: 700; letter-spacing: 0.8px;'>🏅 {title}</p>
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

    # Level progression: pass if >=70% (configurable)
    passed = pct >= 70
    current_level = st.session_state.get("level", 1)
    max_level = st.session_state.get("max_level", 20)

    st.markdown("---")
    level_col1, level_col2, level_col3 = st.columns([1, 1, 1])
    with level_col1:
        if st.button("↻ Try Again", key="play_again_btn", use_container_width=True):
            # replay same level/category
            start_game()
            st.rerun()
    with level_col2:
        if st.session_state.get("level_mode", True):
            if passed and current_level < max_level:
                if st.button(f"Level Up → (Go to Level {current_level+1})", key="level_up_btn", use_container_width=True):
                    st.session_state.level = current_level + 1
                    st.success(f"Congratulations! Advanced to Level {current_level+1}")
                    st.balloons()
                    # keep same category but start next level
                    start_game()
                    st.rerun()
            else:
                if not passed:
                    st.info(f"You needed 70% to level up. Try again to reach Level {current_level+1}.")
                else:
                    st.success("You've reached the maximum level! Great job.")
        else:
            if st.button("→ Next Category", key="change_category_btn", use_container_width=True):
                st.session_state.show_result = False
                st.session_state.game_active = False
                st.session_state.selected_category = None
                st.rerun()
    with level_col3:
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

st.markdown(
        '''
        <div class="topbar">
            <div class="brand">
                <div class="logo">🇳🇱</div>
                <div>
                    <div class="title">Netherlands QuizMaster</div>
                    <div class="subtitle">Quiz</div>
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
        <div class="flag-stripe"></div>
        <div style="margin-top:12px; margin-bottom: 16px;">
            <h2 style='margin: 0; font-weight: 600; font-size: 22px;'>Quiz</h2>
            <p style='margin:6px 0 0 0; color: var(--muted);'>Answer the questions and level up your knowledge.</p>
        </div>
        ''',
        unsafe_allow_html=True,
)

if not st.session_state.player_name:
    show_login()
elif st.session_state.show_result:
    show_logout()
    st.markdown("---")
    show_results()
elif not st.session_state.game_active:
    show_logout()
    st.markdown("---")
    
    # AI Quiz Generation Section
    with st.expander("🤖 Generate AI Quiz", expanded=False):
        st.markdown("Create a custom quiz using AI!")
        ai_category = st.text_input("Topic/Category", placeholder="e.g., History of Netherlands", key="ai_category")
        ai_num = st.slider("Number of questions", 3, 10, 5, key="ai_num")
        ai_difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1, key="ai_difficulty")
        
        if st.button("Generate Quiz", key="generate_ai_quiz"):
            if ai_category.strip():
                with st.spinner("Generating questions with AI..."):
                    ai_questions = generate_questions_with_ai(ai_category.strip(), ai_num, ai_difficulty)
                    if ai_questions:
                        st.session_state.ai_generated_questions = ai_questions
                        st.session_state.selected_category = f"AI: {ai_category}"
                        st.session_state.selected_difficulty = ai_difficulty.capitalize()
                        st.success(f"Generated {len(ai_questions)} questions!")
                        st.rerun()
                    else:
                        st.error("Failed to generate questions. Check your OpenAI API key.")
            else:
                st.error("Please enter a topic.")
    
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

# close page container
st.markdown('</div>', unsafe_allow_html=True)
