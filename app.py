# -*- coding: utf-8 -*-
"""
Recall Agent – Streamlit UI
A polished, light‑theme dashboard that wraps the existing business‑logic
(memory.py, scheduler.py, grader.py) without modifying it.
"""

import os
from datetime import datetime, timedelta
import pandas as pd


import streamlit as st

import memory

import scheduler


import grader

from dotenv import load_dotenv

# Define a shortcut to the default memory file for convenience
MEMORY_FILE = memory.DEFAULT_MEMORY_FILE

# Load environment variables
load_dotenv()


# Helper functions for UI enhancements
def stat_card(value, label):
    """Return HTML for a clean stat card with navy number and muted label."""
    html = f"""
    <div style="background:#FFFFFF; border:1px solid #E5E7EB; border-radius:8px; padding:20px;        <div style='display: flex; align-items: center;'>
            <div style='font-size: 2rem; font-weight: bold; color: #0a0a0a;'>{value}</div>
            <div style='margin-left: 8px; font-size: 1rem; color: #555;'>{label}</div>
        </div>
    """
    return html


def compute_streak(db):
    """Calculate consecutive days with at least one review up to today."""
    reviewed_dates = set()
    for details in db.values():
        for h in details.get("history", []):
            reviewed_dates.add(h["date"][:10])
    today = datetime.now().date()
    streak = 0
    day = today
    while day.isoformat() in reviewed_dates:
        streak += 1
        day -= timedelta(days=1)
    return streak


# --------------------------------------------------------------------------- #
# Configuration & theming
# --------------------------------------------------------------------------- #
MEMORY_FILE = os.getenv("MEMORY_FILE", "memory.json")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# --------------------------------------------------------------------------- #
# Streamlit page config
# --------------------------------------------------------------------------- #

st.set_page_config(
    page_title="Recall Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------- #
# Light theme CSS
# --------------------------------------------------------------------------- #
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-color: #FAF7F2;
    --card-bg: #FFFFFF;
    --text-color: #2C3E50;
    --accent: #2C3E50;
    --border-color: rgba(44, 62, 80, 0.08);
    --muted-grey: #7F8C8D;
}

body, .stApp, p, label, input, textarea, button, select {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: var(--text-color);
}
h1, h2, h3, h4, h5, h6, .hero-header {
    font-family: 'Lora', Georgia, "Times New Roman", serif !important;
    font-weight: 600 !important;
    color: var(--text-color) !important;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

.stCard, .stContainer > div {
    background: var(--card-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 2rem !important;
    box-shadow: none !important;
    margin-bottom: 1.5rem;
}

button[data-testid="stBaseButton-primary"] {
    background: var(--accent) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 500;
    padding: 0.5rem 1.5rem !important;
    transition: background-color 200ms ease, transform 200ms ease !important;
}
button[data-testid="stBaseButton-primary"]:hover {
    background: #71a7d9 !important;
}

button[data-testid="stBaseButton-secondary"] {
    border-radius: 6px !important;
    border: 1px solid var(--border-color) !important;
    background: transparent !important;
    color: var(--text-color) !important;
    transition: background-color 200ms ease, border-color 200ms ease !important;
}
button[data-testid="stBaseButton-secondary"]:hover {
    background: rgba(44, 62, 80, 0.03) !important;
    border-color: rgba(44, 62, 80, 0.15) !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    border-radius: 6px !important;
    border: 1px solid var(--border-color) !important;
    padding: 0.75rem !important;
    background: #ffffff !important;
    color: var(--text-color) !important;
    font-size: 1rem;
    transition: border-color 200ms ease, box-shadow 200ms ease !important;
    box-shadow: none !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent) !important;
}

section[data-testid="stSidebar"] {
    background: #F5F0E6 !important;
    border-right: 1px solid var(--border-color);
}
section[data-testid="stSidebar"] h1 {
    font-size: 1.5rem !important;
}

.metric-card {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    margin-bottom: 1rem !important;
    text-align: left !important;
}
.metric-card h4 {
    margin-top: 0.5rem !important;
    color: var(--muted-grey) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
}
.metric-card p {
    margin: 0 !important;
    color: var(--text-color) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    line-height: 1 !important;
}

.hero-header {
    font-size: 2.8rem;
    font-weight: 700;
    text-align: center;
    margin-top: 0.5rem;
    margin-bottom: 0.25rem;
    color: var(--text-color) !important;
    padding: 0.5rem 0;
}
.sub-header {
    text-align: center;
    color: var(--muted-grey);
    opacity: 0.85;
    margin-bottom: 2rem;
    font-size: 1.15rem;
    font-style: italic;
}

hr {
    border: 0 !important;
    height: 1px !important;
    background: rgba(44, 62, 80, 0.08) !important;
    margin: 2rem 0 !important;
}

.review-question {
    background: #F5F0E6;
    padding: 1.5rem;
    border-radius: 8px;
    border-left: 3px solid var(--accent);
    margin-bottom: 1.5rem;
    font-size: 1.15rem;
    color: var(--text-color);
}

@media (max-width: 768px) {
    .stColumns > div {width: 100% !important; margin-bottom: 1rem;}
}
"""
st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Helper utilities (wrap business logic – unchanged)
# --------------------------------------------------------------------------- #
def _load_memory():
    return memory.load_memory(MEMORY_FILE)


def _save_memory(db):
    memory.save_memory(db, MEMORY_FILE)


def _get_due_concepts(db):
    return memory.get_due_concepts(db)


def _grade_answer(question, expected, user_resp):
    return grader.grade_answer(question, expected, user_resp, GEMINI_API_KEY)


def _safe_int_score(score, fallback=3):
    """
    BUG FIX: Gemini sometimes returns a float (e.g. 3.5) or a string.
    st.select_slider requires the default 'value' to exactly match one of
    the items in 'options' (which are plain ints 0-5). A float/str mismatch
    silently crashes the slider widget. This clamps + casts safely.
    """
    try:
        s = int(round(float(score)))
    except (TypeError, ValueError):
        return fallback
    return max(0, min(5, s))


# --------------------------------------------------------------------------- #
# Sidebar navigation
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.title("🗂️ Recall Agent")
    pages = {
        "📊 Dashboard": "Dashboard",
        "➕ Add Concept": "Add Concept",
        "📖 Review Concepts": "Review Concepts",
        "🛠️ Manage Concepts": "Manage Concepts",
        "📈 Analytics": "Analytics",
    }
    page_display = st.radio("Select page", list(pages.keys()))
    page = pages[page_display]

# --------------------------------------------------------------------------- #
# Hero header (visible on every page)
# --------------------------------------------------------------------------- #
st.markdown(
    """
<div class='hero-header'>🧠 Recall Agent</div>
<div class='sub-header'>AI‑Powered Spaced Repetition Learning</div>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Page: Add Concept
# --------------------------------------------------------------------------- #
if page == "Add Concept":
    st.header("✨ Add a New Concept")
    with st.container():
        concept_name = st.text_input("Concept Name", key="add_concept_name")
        question = st.text_area("Question", key="add_question")
        expected_answer = st.text_area("Expected Answer", key="add_expected_answer")
        if st.button("💾 Save Concept", type="primary"):
            if (
                not concept_name.strip()
                or not question.strip()
                or not expected_answer.strip()
            ):
                st.error("All fields are required.")
            else:
                try:
                    memory.add_concept(
                        concept_name.strip(),
                        question.strip(),
                        expected_answer.strip(),
                        MEMORY_FILE,
                    )
                    st.success(f"✅ Concept **{concept_name}** added successfully!")
                    st.session_state["add_concept_name"] = ""
                    st.session_state["add_question"] = ""
                    st.session_state["add_expected_answer"] = ""
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to add concept: {e}")

# --------------------------------------------------------------------------- #
# Page: Review Concepts
# --------------------------------------------------------------------------- #
elif page == "Review Concepts":
    st.header("🔄 Review Due Concepts")
    db = _load_memory()
    due = _get_due_concepts(db)
    if not due:
        st.success("🎉 No concepts are due for review today!")
    else:
        display_to_name = {name: name for name in due.keys()}
        display_options = list(due.keys())
        concept_keys = list(due.keys())

        # ------------------------------------------------------------------
        # BUG FIX: session-state keys were only initialised INSIDE the
        # "review_concept missing/invalid" branch. If review_concept was
        # already valid but review_stage/user_answer/etc. were missing
        # (e.g. after a hot-reload), later code would crash with
        # AttributeError. Now every key is guaranteed to exist up front,
        # every single run, regardless of branch.
        # ------------------------------------------------------------------
        if (
            "review_concept" not in st.session_state
            or st.session_state.review_concept not in concept_keys
        ):
            st.session_state.review_concept = concept_keys[0]
            st.session_state.review_stage = "input"
            st.session_state.user_answer = ""
            st.session_state.gemini_score = None
            st.session_state.gemini_feedback = ""
            st.session_state.error_occurred = False

        for key, default in [
            ("review_stage", "input"),
            ("user_answer", ""),
            ("gemini_score", None),
            ("gemini_feedback", ""),
            ("error_occurred", False),
        ]:
            if key not in st.session_state:
                st.session_state[key] = default

        selected_display = st.selectbox(
            "Select a concept to review",
            options=display_options,
            index=(
                display_options.index(st.session_state.review_concept)
                if st.session_state.review_concept in display_options
                else 0
            ),
        )
        selected_concept = display_to_name[selected_display]

        # Load the selected concept details
        # Reset stage when the user switches concepts
        if "prev_concept" not in st.session_state:
            st.session_state.prev_concept = st.session_state.review_concept
        elif st.session_state.prev_concept != st.session_state.review_concept:
            st.session_state.review_stage = "input"
            st.session_state.prev_concept = st.session_state.review_concept
            st.session_state.user_answer = ""
            st.session_state.gemini_score = None
            st.session_state.gemini_feedback = ""
            st.session_state.error_occurred = False
            st.rerun()

        st.session_state.review_concept = selected_concept
        details = due[st.session_state.review_concept]

        if st.session_state.review_stage == "input":
            with st.container():
                st.subheader(f"Concept: **{st.session_state.review_concept}**")
                st.markdown(
                    f"<div class='review-question'><strong>Question:</strong> {details['question']}</div>",
                    unsafe_allow_html=True,
                )

                user_answer = st.text_area(
                    "Your Answer",
                    value=st.session_state.user_answer,
                    placeholder="Type your answer here...",
                    height=180,
                )

                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("📝 Submit Answer", type="primary"):
                        if not user_answer.strip():
                            st.warning("Please type an answer before grading.")
                        else:
                            st.session_state.user_answer = user_answer.strip()
                            with st.spinner("AI is grading your response..."):
                                try:
                                    score, feedback = _grade_answer(
                                        details["question"],
                                        details["expected_answer"],
                                        st.session_state.user_answer,
                                    )
                                    st.session_state.gemini_score = _safe_int_score(
                                        score
                                    )
                                    st.session_state.gemini_feedback = feedback
                                    st.session_state.error_occurred = False
                                except Exception as e:
                                    st.session_state.gemini_score = None
                                    st.session_state.gemini_feedback = (
                                        f"Failed to grade answer automatically: {e}"
                                    )
                                    st.session_state.error_occurred = True

                            st.session_state.review_stage = "graded"
                            st.rerun()

        elif st.session_state.review_stage == "graded":
            with st.container():
                st.subheader(f"Review Results: **{st.session_state.review_concept}**")
                st.markdown(f"**Question:** {details['question']}")
                st.markdown(f"**Your Answer:** {st.session_state.user_answer}")

                st.markdown("---")
                st.markdown(
                    f"**Expected Answer / Key Points:**\n> {details['expected_answer']}"
                )
                st.markdown("---")

                st.markdown("### 🤖 Gemini Auto-Grading")
                if st.session_state.error_occurred:
                    st.warning(f"⚠️ {st.session_state.gemini_feedback}")
                    st.info(
                        "API grading was unavailable. Please select your manual grade below to proceed."
                    )
                else:
                    score = st.session_state.gemini_score
                    st.markdown(
                        f"""
                    <div class='metric-card' style='max-width: 220px; margin-bottom: 1rem; text-align: center;'>
                        <p>{score}/5</p>
                        <h4>Gemini Grade</h4>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                    if score < 5:
                        st.warning(
                            f"**Why your answer was imperfect / Feedback:**\n\n{st.session_state.gemini_feedback}"
                        )
                    else:
                        st.success(
                            f"**Excellent!**\n\n{st.session_state.gemini_feedback}"
                        )

                st.markdown("---")
                st.markdown("### 🎚️ Submit Final Grade")

                # BUG FIX: cast/clamp again here as a second safety net,
                # since this is the exact line that previously crashed
                # select_slider when gemini_score was a float/str/None.
                default_score = _safe_int_score(
                    st.session_state.gemini_score, fallback=3
                )

                score_options = {
                    5: "5 - Perfect response (fully correct, complete)",
                    4: "4 - Correct response after hesitation / minor omissions",
                    3: "3 - Correct response, but with significant omissions",
                    2: "2 - Incorrect response, but seemed easy to recall",
                    1: "1 - Incorrect response, but recalled the concept name",
                    0: "0 - Complete blackout / completely wrong",
                }

                chosen_score = st.select_slider(
                    "How well did you do? (Adjust the slider if you want to override the AI grade)",
                    options=[0, 1, 2, 3, 4, 5],
                    value=default_score,
                    format_func=lambda x: score_options[x],
                )

                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("💾 Submit & Next", type="primary"):
                        new_interval, new_easiness, new_reps = (
                            scheduler.calculate_next_review(
                                chosen_score,
                                details.get("easiness", 2.5),
                                details.get("repetitions", 0),
                                details.get("interval", 0),
                            )
                        )
                        today = datetime.now()
                        next_review = (today + timedelta(days=new_interval)).strftime(
                            "%Y-%m-%d"
                        )

                        review_entry = {
                            "date": today.strftime("%Y-%m-%d %H:%M:%S"),
                            "user_answer": st.session_state.user_answer,
                            "grade_quality": chosen_score,
                            "feedback": (
                                st.session_state.gemini_feedback
                                if not st.session_state.error_occurred
                                else "Manually graded by user."
                            ),
                        }

                        db[st.session_state.review_concept]["easiness"] = new_easiness
                        db[st.session_state.review_concept]["interval"] = new_interval
                        db[st.session_state.review_concept]["repetitions"] = new_reps
                        db[st.session_state.review_concept]["next_review"] = next_review
                        db[st.session_state.review_concept].setdefault(
                            "history", []
                        ).append(review_entry)

                        _save_memory(db)

                        if DISCORD_WEBHOOK_URL:
                            try:
                                import messenger

                                discord_message = f"🧠 **Recall Agent Review Logged!**\n**Concept:** {st.session_state.review_concept}\n**Grade:** {chosen_score}/5\n**Next Review:** {next_review}"
                                messenger.send_to_discord(
                                    DISCORD_WEBHOOK_URL, discord_message
                                )
                            except Exception:
                                pass

                        st.session_state.review_stage = "input"
                        st.session_state.user_answer = ""
                        st.session_state.gemini_score = None
                        st.session_state.gemini_feedback = ""
                        st.session_state.error_occurred = False

                        remaining = [
                            k
                            for k in concept_keys
                            if k != st.session_state.review_concept
                        ]
                        if remaining:
                            st.session_state.review_concept = remaining[0]
                        else:
                            if "review_concept" in st.session_state:
                                del st.session_state.review_concept

                        st.success("Successfully updated concept scheduling!")
                        st.rerun()
                with col2:
                    if st.button("↩️ Re-enter Answer"):
                        st.session_state.review_stage = "input"
                        st.session_state.user_answer = ""
                        st.rerun()

        with st.expander("📜 View Review History for this Concept"):
            history = details.get("history", [])
            if not history:
                st.info("No reviews recorded yet for this concept.")
            else:
                for idx, entry in enumerate(reversed(history)):
                    st.markdown(
                        f"**Attempt {len(history) - idx}** ({entry.get('date', 'N/A')}):"
                    )
                    st.markdown(f"- **Grade:** {entry.get('grade_quality', 0)}/5")
                    st.markdown(f"- **Your Answer:** {entry.get('user_answer', 'N/A')}")
                    st.markdown(f"- **Feedback:** {entry.get('feedback', 'N/A')}")
                    st.markdown("---")

# --------------------------------------------------------------------------- #
# Page: Dashboard (quick overview)
# --------------------------------------------------------------------------- #
elif page == "Dashboard":
    # No logo column – just the title column
    col_title = st.columns([5])[0]
    with col_title:
        st.markdown(
            "<h2 style='margin-top: 10px; margin-bottom: 0px;'>Welcome to Recall Agent!</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='font-size: 1.1rem; color: #6e6e6e; margin-top: 5px;'>"
            "Never forget what you learn — your AI agent remembers for you."
            "</p>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    db = _load_memory()
    total_concepts = len(db)
    today_str = datetime.now().strftime("%Y-%m-%d")
    concepts_due_today = sum(
        1 for v in db.values() if v.get("next_review") and v.get("next_review") <= today_str
    )
    total_reviews = sum(len(v.get("history", [])) for v in db.values())
    avg_easiness = (
        round(
            sum(v.get("easiness", 2.5) for v in db.values()) / max(total_concepts, 1),
            2,
        )
        if total_concepts
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(stat_card(total_concepts, "Total Concepts"), unsafe_allow_html=True)
    with col2:
        st.markdown(stat_card(concepts_due_today, "Due Today"), unsafe_allow_html=True)
    with col3:
        st.markdown(stat_card(total_reviews, "Total Reviews"), unsafe_allow_html=True)
    with col4:
        st.markdown(stat_card(avg_easiness, "Avg. Easiness"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📅 Today's Focus")

    if concepts_due_today > 0:
        st.warning(
            f"🔔 You have **{concepts_due_today}** concept(s) due for review today. Go to the **📖 Review Concepts** tab to review them!"
        )
        due_list = [k for k, v in db.items() if v.get("next_review") and v.get("next_review") <= today_str]
        st.markdown("**Due Concepts:** " + ", ".join([f"`{c}`" for c in due_list]))
    else:
        st.success(
            "🎉 All caught up! No reviews due today. You can add new concepts or view analytics."
        )

# --------------------------------------------------------------------------- #
# Page: Manage Concepts
# --------------------------------------------------------------------------- #
elif page == "Manage Concepts":
    st.header("🛠️ Manage Concepts")
    db = _load_memory()
    if not db:
        st.info("No concepts added yet. Go to **➕ Add Concept** to create one.")
    else:
        for concept_name, details in db.items():
            with st.expander(f"📌 **{concept_name}**"):
                st.markdown(f"**Question:** {details['question']}")
                new_ans = st.text_area(
                    "Expected Answer",
                    value=details["expected_answer"],
                    key=f"edit_{concept_name}",
                    height=100,
                )

                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("💾 Update", key=f"btn_edit_{concept_name}"):
                        memory.update_concept(concept_name, new_ans, MEMORY_FILE)
                        st.success(f"Updated '{concept_name}'!")
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"del_{concept_name}"):
                        memory.delete_concept(concept_name, MEMORY_FILE)
                        st.success(f"Concept '{concept_name}' deleted!")
                        st.rerun()

                st.markdown("---")
                st.markdown("**Review History:**")
                history = details.get("history", [])
                if not history:
                    st.info("No reviews recorded yet for this concept.")
                else:
                    for idx, entry in enumerate(reversed(history)):
                        st.markdown(
                            f"**Attempt {len(history) - idx}** ({entry.get('date', 'N/A')}):"
                        )
                        st.markdown(f"- **Grade:** {entry.get('grade_quality', 0)}/5")
                        st.markdown(
                            f"- **Your Answer:** {entry.get('user_answer', 'N/A')}"
                        )
                        st.markdown(f"- **Feedback:** {entry.get('feedback', 'N/A')}")
                        st.markdown("<br>", unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# Page: Analytics (full statistics & charts)
# --------------------------------------------------------------------------- #
elif page == "Analytics":
    st.header("📈 Analytics")
    db = _load_memory()
    total_concepts = len(db)
    today_str = datetime.now().strftime("%Y-%m-%d")
    concepts_due_today = sum(
        1 for v in db.values() if v.get("next_review") == today_str
    )
    total_reviews = sum(len(v.get("history", [])) for v in db.values())
    avg_easiness = (
        round(
            sum(v.get("easiness", 2.5) for v in db.values()) / max(total_concepts, 1),
            2,
        )
        if total_concepts
        else 0
    )
    correct_reviews = sum(
        1
        for v in db.values()
        for h in v.get("history", [])
        if h.get("grade_quality", 0) >= 3
    )
    incorrect_reviews = sum(
        1
        for v in db.values()
        for h in v.get("history", [])
        if h.get("grade_quality", 0) < 3
    )
    if db:
        strongest = max(db.items(), key=lambda i: i[1].get("easiness", 2.5))[0]
        weakest = min(db.items(), key=lambda i: i[1].get("easiness", 2.5))[0]
    else:
        strongest = weakest = "N/A"

    row1_col1, row1_col2, row1_col3 = st.columns(3)
    with row1_col1:
        st.markdown(
            f"<div class='metric-card'><p>{total_concepts}</p><h4>Total Concepts</h4></div>",
            unsafe_allow_html=True,
        )
    with row1_col2:
        st.markdown(
            f"<div class='metric-card'><p>{concepts_due_today}</p><h4>Due Today</h4></div>",
            unsafe_allow_html=True,
        )
    with row1_col3:
        st.markdown(
            f"<div class='metric-card'><p>{total_reviews}</p><h4>Total Reviews</h4></div>",
            unsafe_allow_html=True,
        )

    row2_col1, row2_col2, row2_col3 = st.columns(3)
    with row2_col1:
        st.markdown(
            f"<div class='metric-card'><p>{avg_easiness}</p><h4>Avg. Easiness</h4></div>",
            unsafe_allow_html=True,
        )
    with row2_col2:
        st.markdown(
            f"<div class='metric-card'><p style='color: #2e7d32 !important;'>{correct_reviews}</p><h4>Correct (≥3)</h4></div>",
            unsafe_allow_html=True,
        )
    with row2_col3:
        st.markdown(
            f"<div class='metric-card'><p style='color: #c62828 !important;'>{incorrect_reviews}</p><h4>Incorrect (<3)</h4></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.subheader("Concept Performance")
    col_str, col_weak = st.columns(2)
    with col_str:
        st.markdown(
            f"""
        <div style='border-left: 3px solid #2e7d32; padding-left: 1.25rem; margin-bottom: 1rem;'>
            <h4 style='margin:0; color: #7F8C8D; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; font-family: "Inter", sans-serif;'>🌟 Strongest Concept</h4>
            <p style='margin: 0.25rem 0 0 0; font-size: 1.35rem; font-weight: 600; color: #2C3E50; font-family: "Lora", serif;'>{strongest}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col_weak:
        st.markdown(
            f"""
        <div style='border-left: 3px solid #c62828; padding-left: 1.25rem; margin-bottom: 1rem;'>
            <h4 style='margin:0; color: #7F8C8D; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; font-family: "Inter", sans-serif;'>⚠️ Weakest Concept</h4>
            <p style='margin: 0.25rem 0 0 0; font-size: 1.35rem; font-weight: 600; color: #2C3E50; font-family: "Lora", serif;'>{weakest}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    if db:
        st.markdown("---")
        st.subheader("📊 Concept Easiness Factor")
        easiness_vals = [v.get("easiness", 2.5) for v in db.values()]
        concept_names = list(db.keys())
        chart_df = pd.DataFrame({"Concept": concept_names, "Easiness": easiness_vals})
        st.bar_chart(chart_df.set_index("Concept"))

        dates = []
        for v in db.values():
            for h in v.get("history", []):
                dates.append(h["date"][:10])
        if dates:
            st.markdown("---")
            st.subheader("📈 Review Activity Over Time")
            rev_df = pd.DataFrame(pd.Series(dates).value_counts().sort_index())
            rev_df.columns = ["Reviews Completed"]
            st.line_chart(rev_df)

# --------------------------------------------------------------------------- #
# Footer (branding)
# --------------------------------------------------------------------------- #
st.sidebar.markdown("---")
st.sidebar.caption("Recall Agent – AI‑powered spaced repetition\nVersion 1.0")
