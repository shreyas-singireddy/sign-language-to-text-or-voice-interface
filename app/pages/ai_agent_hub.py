import streamlit as st

from ai_engine.ai_agent.learning_coach import learning_coach
from ai_engine.ai_agent.llm_engine import llm_engine
from ai_engine.ai_agent.rag_engine import rag_engine
from database.learning_schemas import learning_db
from src.services.translation_service import t

# Page headers
st.markdown(
    f'<h1 class="gradient-text" style="font-size: 3.5rem; margin-bottom: 5px; letter-spacing: -2px;">{t("sidebar_home").upper()} AI HUB</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size: 1.25rem; font-weight: 700; color: #1040C0; text-transform: uppercase;'>SignBridge AI Agent Cockpit & Personalized Learning Coach</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# User details from session state
user_phone = st.session_state.get("user_phone", "demo_user")
user_lang = st.session_state.get("language", "English")

# Tabs layout
tab_coach, tab_rag, tab_models = st.tabs(
    ["🏋️ AI Learning Coach", "📚 AI Knowledge Base (RAG)", "⚙️ Local Model Settings"]
)

# ----------------- TAB 1: AI LEARNING COACH -----------------
with tab_coach:
    col_stats, col_quiz = st.columns([1, 1])

    with col_stats:
        st.markdown("### Learning Progress Profile")

        # Load user progress from DB
        progress = learning_db.get_progress(user_phone)

        st.markdown(
            f"""
            <div class="bauhaus-card card-red" style="padding: 20px; margin-bottom: 20px;">
                <h4 style="margin: 0 0 10px 0; font-size: 1.1rem; color: #D02020 !important;">SKILL LEVEL</h4>
                <h1 style="font-size: 3rem; margin: 0; letter-spacing: -2px;">{progress.get('skill_level', 'Novice')}</h1>
                <div style="margin-top: 15px; font-weight: bold;">
                    <p style="margin: 5px 0;">🎯 Practice Count: {progress.get('practice_count', 0)} sessions</p>
                    <p style="margin: 5px 0;">📈 Average Accuracy: {int(progress.get('average_accuracy', 0.0) * 100)}%</p>
                    <p style="margin: 5px 0;">🔥 Practice Streak: {progress.get('streak', 0)} days</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Daily Challenge
        challenge = learning_coach.get_daily_challenge(user_phone, user_lang)
        st.markdown("### Daily Challenge")
        st.markdown(
            f"""
            <div class="bauhaus-card card-yellow" style="padding: 15px;">
                <h4 style="margin: 0; font-size: 1rem;">🎯 CHALLENGE OF THE DAY</h4>
                <p style="font-size: 1.15rem; font-weight: bold; margin-top: 10px;">{challenge['description']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Weak signs
        st.markdown("### Weak Signs (Needs Practice)")
        weak_signs = progress.get("weak_signs", [])
        if weak_signs:
            st.write(", ".join([f"`{sign}`" for sign in weak_signs]))
        else:
            st.info("No weak signs registered. Keep up the high accuracy!")

    with col_quiz:
        st.markdown("### Sign Language Quiz")
        st.write(
            "Test your knowledge of sign gestures and pipeline settings. The questions will adapt to your weak areas."
        )

        # Setup session state for quizzes
        if "active_quiz" not in st.session_state:
            st.session_state["active_quiz"] = None
        if "quiz_answers" not in st.session_state:
            st.session_state["quiz_answers"] = {}
        if "quiz_score" not in st.session_state:
            st.session_state["quiz_score"] = None

        if st.button("Generate Dynamic Quiz", key="btn_gen_quiz"):
            with st.spinner("Compiling practice quiz..."):
                quiz = learning_coach.generate_quiz(user_phone, user_lang, num_questions=3)
                st.session_state["active_quiz"] = quiz
                st.session_state["quiz_answers"].clear()
                st.session_state["quiz_score"] = None

        active_quiz = st.session_state["active_quiz"]
        if active_quiz:
            questions = active_quiz["questions"]
            quiz_id = active_quiz["quiz_id"]

            # Render Quiz form
            st.write("---")
            for idx, q in enumerate(questions):
                st.markdown(f"**Q{idx+1}: {q['question_text']}**")
                ans = st.radio(f"Select answer for Q{idx+1}", options=q["options"], key=f"q_{quiz_id}_{idx}")
                st.session_state["quiz_answers"][idx] = ans
                st.write("")

            if st.button("Submit Quiz Answers", key="btn_submit_quiz"):
                score = 0
                for idx, q in enumerate(questions):
                    selected = st.session_state["quiz_answers"].get(idx)
                    if selected == q["correct_answer"]:
                        score += 1

                percentage = int((score / len(questions)) * 100)
                st.session_state["quiz_score"] = percentage

                # Save score to DB
                learning_db.submit_quiz(quiz_id, percentage)

            if st.session_state["quiz_score"] is not None:
                score_val = st.session_state["quiz_score"]
                st.success(f"Quiz Completed! Your Score: **{score_val}%**")
                if score_val >= 80:
                    st.balloons()

# ----------------- TAB 2: AI KNOWLEDGE BASE (RAG) -----------------
with tab_rag:
    st.markdown("### Ask the SignBridge AI Knowledge Base")
    st.write(
        "This search engine is indexed directly on project documentation blueprints. Ask how sign models, database pools, or CV cameras function."
    )

    if "rag_chat_history" not in st.session_state:
        st.session_state["rag_chat_history"] = []

    user_query = st.text_input(
        "Ask a question about the project:", placeholder="e.g. How does the temporal sequence model predict words?"
    )

    if st.button("Submit Query", key="btn_query_rag"):
        if user_query.strip():
            with st.spinner("Searching master documentation and generating answer..."):
                # Retrieve context chunks
                context = rag_engine.retrieve_context(user_query, top_k=2)

                # Format prompts
                prompt = (
                    f"Answer the user's question: '{user_query}'\n\n"
                    f"Relevant Documentation Context:\n{context}\n\n"
                    "Ensure your response is clear, formatted in markdown, and explains the architecture standard."
                )
                system_prompt = "You are an expert technical assistant specializing in SignBridge AI system codebase."

                answer = llm_engine.generate_completion(prompt, system_prompt=system_prompt)

                # Append to history
                st.session_state["rag_chat_history"].insert(0, {"question": user_query, "answer": answer})

    # Render History
    if st.session_state["rag_chat_history"]:
        st.write("---")
        for chat in st.session_state["rag_chat_history"]:
            st.markdown(f"#### ❓ {chat['question']}")
            st.markdown(chat["answer"])
            st.markdown("---")

# ----------------- TAB 3: LOCAL MODEL SETTINGS -----------------
with tab_models:
    st.markdown("### AI Model Configuration Cockpit")
    st.write("Configure offline capabilities and select active deep learning models.")

    # Check Ollama Availability
    ollama_ok = llm_engine.is_ollama_available()

    if ollama_ok:
        st.success("● LOCAL OLLAMA SERVER: ONLINE")
    else:
        st.warning("⚠️ LOCAL OLLAMA SERVER: OFFLINE (Running in Gemini Cloud fallback mode)")

    st.markdown("### Selected Inference Engine")
    selected_model = st.selectbox(
        "Active LLM Model",
        options=["qwen2.5", "gemma2", "llama3", "mistral", "Google Gemini (Cloud)"],
        index=0 if ollama_ok else 4,
        key="select_active_llm",
    )

    st.markdown("---")
    st.markdown("### Local RAG Index Status")

    # Reload documents button
    if st.button("Re-index Master Documents", key="btn_rag_reindex"):
        with st.spinner("Indexing documentation files..."):
            rag_engine.load_and_index()
            st.success("Documentation index rebuilt successfully!")

    st.write(f"- Indexed Chunks: `{len(rag_engine.chunks) if rag_engine.chunks else 0}` chunks loaded.")
    st.write(f"- Documentation Directory: `{rag_engine.chunks[0]['file'] if rag_engine.chunks else 'Not Indexed'}`")
