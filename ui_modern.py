import streamlit as st
import random
import time
from style import get_modern_css
from config import AVAILABLE_MODELS
from processor import extract_text, generate_quiz_dynamic
from db import save_quiz_to_db

def init_state():
    defaults = {
        'quiz_data': None,
        'current_idx': 0,
        'score': 0,
        'answers_log': {},      # {idx: {'user_ans': 'A', 'is_correct': True}}
        'shuffled_opts': {},    # {idx: [(index_asli, teks_opsi), ...]}
        'app_mode': 'setup'     # setup | game | summary
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def get_options_shuffled(idx, options):
    """Mengembalikan opsi yang sudah diacak dan konsisten"""
    if idx not in st.session_state.shuffled_opts:
        indexed = list(enumerate(options)) # [(0, 'Benar'), (1, 'Salah1')...]
        random.shuffle(indexed)
        st.session_state.shuffled_opts[idx] = indexed
    return st.session_state.shuffled_opts[idx]

def render_app_modern():
    st.markdown(get_modern_css(), unsafe_allow_html=True)
    init_state()

    # Routing sederhana
    if st.session_state.app_mode == 'setup':
        render_setup()
    elif st.session_state.app_mode == 'game':
        render_game()
    elif st.session_state.app_mode == 'summary':
        render_summary()

def render_setup():
    st.markdown("## Quiz Generator")
    
    # Input Area
    with st.container(border=True):
        tab1, tab2 = st.tabs(["Upload", "Text"])
        context = ""
        topic = ""
        
        with tab1:
            f = st.file_uploader("Source File", type=['pdf', 'txt', 'md'], label_visibility="collapsed")
            if f:
                context = extract_text(f)
                topic = f.name
        with tab2:
            txt = st.text_area("Paste Content", height=150, label_visibility="collapsed")
            if txt:
                context = txt
                topic = "Manual Input"

    # Config Area
    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox("Engine", list(AVAILABLE_MODELS.keys()))
    with col2:
        count = st.number_input("Total Questions", min_value=1, value=5)

    if st.button("Start Session", type="primary", use_container_width=True):
        if not context:
            st.toast("Please provide content first.", icon="⚠️")
            return
            
        with st.spinner("Analyzing content & generating questions..."):
            cfg = {"model_id": AVAILABLE_MODELS[model], "q_count": count, "mode": "Modern Drill"}
            res = generate_quiz_dynamic(context, cfg)
            
            if "error" in res:
                st.error("Failed to generate quiz.")
            else:
                st.session_state.quiz_data = res
                st.session_state.app_mode = 'game'
                st.rerun()

def render_game():
    data = st.session_state.quiz_data
    curr = st.session_state.current_idx
    total = len(data)
    
    # Progress Bar Minimalis
    st.progress((curr) / total, text=f"Question {curr + 1} / {total}")
    
    # Ambil soal
    q = data[curr]
    question_text = q.get('question', 'No question')
    opts_raw = q.get('options', [])
    shuffled = get_options_shuffled(curr, opts_raw)
    
    # --- QUESTION CARD (HTML Injection for Class) ---
    st.markdown(f"""
    <div class='animate-card question-card'>
        <div class='question-meta'>Topic: Quiz Analysis</div>
        <div class='question-text'>{question_text}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- INTERACTION AREA ---
    # Cek apakah user sudah menjawab soal ini sebelumnya
    has_answered = curr in st.session_state.answers_log
    
    # Form Container
    placeholder = st.empty()
    
    if not has_answered:
        with placeholder.form(key=f"q_form_{curr}"):
            # Tampilkan opsi
            display_opts = [txt for idx, txt in shuffled]
            choice = st.radio("Select Answer:", display_opts, label_visibility="collapsed", key=f"radio_{curr}")
            
            if st.form_submit_button("Check Answer", use_container_width=True, type="primary"):
                # Logic Cek Jawaban
                selected_idx = -1
                for idx, txt in shuffled:
                    if txt == choice:
                        selected_idx = idx
                        break
                
                is_correct = (selected_idx == 0) # Asumsi index 0 selalu jawaban benar dr backend
                
                # Simpan log
                st.session_state.answers_log[curr] = {
                    'user_ans': choice,
                    'is_correct': is_correct,
                    'correct_txt': opts_raw[0]
                }
                
                if is_correct: st.session_state.score += 1
                st.rerun() # Refresh untuk memunculkan tampilan 'Answered'
                
    else:
        # --- RESULT VIEW (TAMPIL SETELAH JAWAB) ---
        log = st.session_state.answers_log[curr]
        explanation = q.get('explanation', 'No explanation provided.')
        
        # 1. Status Card (Feedback Langsung)
        if log['is_correct']:
            st.markdown(f"""
            <div class='result-container animate-card status-card-correct'>
                <span>✅</span> Correct Answer
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='result-container animate-card'>
                <div class='status-card-wrong'>
                    <span>❌</span> Incorrect.
                </div>
                <div style='background: #1e232e; padding: 12px; border-radius: 8px; border: 1px solid #da3633; color: #fff;'>
                    <small style='color: #8b949e'>Correct Answer:</small><br>
                    {log['correct_txt']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # 2. Explanation Card (Terpisah)
        st.markdown(f"""
        <div class='result-container animate-card' style='animation-delay: 0.1s'>
            <div class='explanation-card'>
                <strong style='color: #58a6ff; display: block; margin-bottom: 8px;'>Why is this correct?</strong>
                {explanation}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        col_nav = st.columns([3, 1])
        with col_nav[1]:
            if curr < total - 1:
                if st.button("Next ❯", type="primary"):
                    st.session_state.current_idx += 1
                    st.rerun()
            else:
                if st.button("Finish", type="primary"):
                    st.session_state.app_mode = 'summary'
                    st.rerun()

def render_summary():
    score = st.session_state.score
    total = len(st.session_state.quiz_data)
    
    st.markdown("<div class='animate-card question-card' style='text-align:center'>", unsafe_allow_html=True)
    st.subheader("Session Complete")
    st.metric("Final Score", f"{score}/{total}")
    
    if st.button("Start New Session", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
