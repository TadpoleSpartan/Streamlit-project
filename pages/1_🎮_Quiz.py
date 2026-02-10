import streamlit as st
import json
import random
import time
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Quiz - Netherlands QuizMaster", page_icon="🎮", layout="wide")

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
        "achievements": []
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

def check_answer(selected_index: int):
    q = st.session_state.questions[st.session_state.current_question_index]
    st.session_state.answered_current = True
    st.session_state.selected_answer = selected_index

    correct = q["correct"]
    base = q.get("points", 10)

    if selected_index == correct:
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

    # header metrics
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Score", st.session_state.score)
    c2.metric("Correct", st.session_state.correct_answers)
    c3.metric("Streak", st.session_state.current_streak)
    c4.metric("Multiplier", f"{st.session_state.multiplier}x")
    c5.metric("Progress", f"{idx+1}/{len(questions)}")

    st.progress((idx+1)/len(questions))

    st.markdown(f"<div class='question-box'><h3>{q['question']}</h3></div>", unsafe_allow_html=True)
    st.caption(f"Difficulty: {q.get('difficulty','unknown').title()} • Base: {q.get('points',10)} pts")

    # power-ups
    p1, p2, p3 = st.columns([1,1,4])
    with p1:
        if st.button(f"💡 Hint ({st.session_state.hints_available})", key="hint"):
            if st.session_state.hints_available > 0 and not st.session_state.answered_current:
                st.session_state.hints_available -= 1
                # reveal one wrong option
                wrongs = [ (i,o) for i,o in enumerate(q['options']) if i != q['correct']]
                if wrongs:
                    i,o = random.choice(wrongs)
                    st.info(f"Hint: it's not '{o}'")
            else:
                st.warning("No hints left or question already answered.")
    with p2:
        if st.button(f"⏭️ Skip ({st.session_state.skips_available})", key="skip"):
            if st.session_state.skips_available > 0 and not st.session_state.answered_current:
                st.session_state.skips_available -= 1
                st.session_state.current_streak = 0
                st.session_state.multiplier = 1.0
                st.warning("Question skipped. Streak reset.")
                time.sleep(0.8)
                next_question()
                st.rerun()
            else:
                st.warning("No skips left or already answered.")
    with p3:
        st.write("")

    st.markdown("---")

    if not st.session_state.answered_current:
        for i,opt in enumerate(q['options']):
            if st.button(f"{chr(65+i)}. {opt}", key=f"opt_{i}"):
                correct = check_answer(i)
                st.experimental_rerun()
    else:
        # show answers and explanation
        for i,opt in enumerate(q['options']):
            prefix = chr(65+i)
            if i == q['correct']:
                st.success(f"{prefix}. {opt}  ✓")
            elif i == st.session_state.selected_answer:
                st.error(f"{prefix}. {opt}  ✗")
            else:
                st.write(f"{prefix}. {opt}")

        if 'explanation' in q:
            st.info(f"Learn more: {q['explanation']}")

        # next button
        if st.button("Next →"):
            next_question()
            st.experimental_rerun()

def show_results():
    total = len(st.session_state.questions)
    correct = st.session_state.correct_answers
    score = st.session_state.score
    time_taken = st.session_state.total_time

    st.header("🏆 Quiz Complete!")
    col1, col2, col3 = st.columns(3)
    col1.metric("Final Score", score)
    col2.metric("Correct", f"{correct}/{total}")
    col3.metric("Time (s)", time_taken)

    pct = (correct/total*100) if total>0 else 0
    if pct >= 90:
        st.success("Legendary! You know the Netherlands well!")
        st.balloons()
    elif pct >= 70:
        st.success("Great job!")
    elif pct >= 50:
        st.warning("Not bad — keep learning!")
    else:
        st.info("Keep practicing — you'll get better!")

    st.markdown("---")
    if st.button("Play Again"):
        start_game()
        st.experimental_rerun()
    if st.button("Back to Home"):
        st.session_state.show_result = False
        st.session_state.game_active = False
        st.experimental_rerun()

# ============== MAIN ==============

st.title("🎮 Netherlands Quiz - Challenge")

if not st.session_state.player_name:
    st.warning("Please enter your name on the Home page first.")
    if st.button("Go to Home"):
        st.switch_page("Home.py")
elif st.session_state.show_result:
    show_results()
elif not st.session_state.game_active:
    st.write(f"Welcome, **{st.session_state.player_name}**")
    if st.session_state.selected_category:
        st.write(f"Category: **{st.session_state.selected_category}**")
        if st.button("Start Quiz"):
            start_game()
            st.experimental_rerun()
    else:
        st.info("Select a category on Home or Categories page first.")
        if st.button("Go to Categories"):
            st.switch_page("pages/3_📚_Categories.py")
else:
    show_question()
