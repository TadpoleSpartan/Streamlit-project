import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Question Editor - QuizMaster", page_icon="✏️")
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
QUESTIONS_FILE = DATA_DIR / "questions.json"
CSS_FILE = ROOT / "assets" / "styles.css"
if CSS_FILE.exists():
    st.markdown(f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

st.markdown("<h1 style='margin-bottom:8px;'>Question Editor</h1>", unsafe_allow_html=True)

# Helpers

def load_questions():
    if QUESTIONS_FILE.exists():
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"categories": {}}


def save_questions(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


data = load_questions()
categories = list(data.get('categories', {}).keys())

col1, col2 = st.columns([3,1])
with col1:
    st.markdown("### Categories")
    if categories:
        cat = st.selectbox("Choose category to manage", categories)
    else:
        st.info("No categories yet. Add one below.")
        cat = None
with col2:
    st.markdown("### Actions")
    new_cat = st.text_input("New category name", key="new_cat")
    if st.button("Add Category") and new_cat.strip():
        if new_cat in categories:
            st.warning("Category already exists")
        else:
            data.setdefault('categories', {})[new_cat] = []
            save_questions(data)
            st.success(f"Added category '{new_cat}'")
            st.experimental_rerun()

st.markdown("---")

if cat:
    st.markdown(f"## Manage: {cat}")
    qlist = data['categories'].get(cat, [])
    if qlist:
        # Show list with edit shortcut
        idx = st.selectbox("Select question to preview / edit", options=list(range(len(qlist))), format_func=lambda i: f"Q{i+1}: {qlist[i].get('question','(no text)')}")
        q = qlist[idx]
        st.markdown(f"**Preview — Q{idx+1}**")
        st.write(f"Points: {q.get('points', 10)} — Difficulty: {q.get('difficulty','medium')}")
        st.write("Options:")
        for oi, opt in enumerate(q.get('options', [])):
            mark = "(Correct)" if oi == q.get('correct') else ""
            st.write(f"{chr(65+oi)}. {opt} {mark}")
        st.write("Explanation:")
        st.write(q.get('explanation', ''))

        col_a, col_b = st.columns([1,1])
        with col_a:
            if st.button(f"Delete Q{idx+1}", key=f"del_{cat}_{idx}"):
                qlist.pop(idx)
                data['categories'][cat] = qlist
                save_questions(data)
                st.success("Question deleted")
                st.experimental_rerun()
        with col_b:
            if st.button(f"Edit Q{idx+1}", key=f"edit_{cat}_{idx}"):
                st.session_state['_editing'] = idx
                st.experimental_rerun()

        # If in edit mode, show edit form
        if st.session_state.get('_editing') is not None:
            edit_idx = st.session_state.get('_editing')
            if edit_idx < 0 or edit_idx >= len(qlist):
                st.session_state['_editing'] = None
            else:
                q_edit = qlist[edit_idx]
                st.markdown("---")
                st.markdown(f"### Edit Q{edit_idx+1}")
                with st.form(key=f"edit_q_{cat}_{edit_idx}"):
                    qtext = st.text_area("Question text", value=q_edit.get('question',''), height=80)
                    opts = st.text_area("Options (one per line)", value='\n'.join(q_edit.get('options',[])))
                    correct = st.number_input("Correct option index (0-based)", min_value=0, step=1, value=int(q_edit.get('correct',0)))
                    points = st.number_input("Points", min_value=1, step=1, value=int(q_edit.get('points',10)))
                    difficulty = st.selectbox("Difficulty", ["easy","medium","hard"], index=["easy","medium","hard"].index(q_edit.get('difficulty','medium')))
                    explanation = st.text_area("Explanation (optional)", value=q_edit.get('explanation',''))
                    submitted = st.form_submit_button("Update Question")
                    if submitted:
                        options = [o.strip() for o in opts.splitlines() if o.strip()]
                        if not qtext.strip() or len(options) < 2:
                            st.error("Please provide a question and at least two options")
                        elif correct >= len(options):
                            st.error("Correct index out of range")
                        else:
                            q_edit.update({
                                'question': qtext.strip(),
                                'options': options,
                                'correct': int(correct),
                                'points': int(points),
                                'difficulty': difficulty,
                            })
                            if explanation.strip():
                                q_edit['explanation'] = explanation.strip()
                            else:
                                q_edit.pop('explanation', None)
                            data['categories'][cat][edit_idx] = q_edit
                            save_questions(data)
                            st.success("Question updated")
                            st.session_state['_editing'] = None
                            st.experimental_rerun()
    else:
        st.info("No questions in this category yet.")

    st.markdown("---")
    st.markdown("### Add New Question")
    with st.form(key=f"add_q_{cat}"):
        qtext = st.text_area("Question text", height=80)
        opts = st.text_area("Options (one per line)")
        correct = st.number_input("Correct option index (0-based)", min_value=0, step=1, value=0)
        points = st.number_input("Points", min_value=1, step=1, value=10)
        difficulty = st.selectbox("Difficulty", ["easy","medium","hard"], index=1)
        explanation = st.text_area("Explanation (optional)")
        submitted = st.form_submit_button("Add Question")
        if submitted:
            options = [o.strip() for o in opts.splitlines() if o.strip()]
            if not qtext.strip() or len(options) < 2:
                st.error("Please provide a question and at least two options")
            elif correct >= len(options):
                st.error("Correct index out of range")
            else:
                entry = {
                    "question": qtext.strip(),
                    "options": options,
                    "correct": int(correct),
                    "points": int(points),
                    "difficulty": difficulty,
                }
                if explanation.strip():
                    entry['explanation'] = explanation.strip()
                data.setdefault('categories', {}).setdefault(cat, []).append(entry)
                save_questions(data)
                st.success("Question added")
                st.experimental_rerun()

st.markdown("---")
if st.button("← Back to Home"):
    st.experimental_set_query_params()
    st.switch_page("Home.py")
