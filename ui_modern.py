import streamlit as st
import random
import time
from config import AVAILABLE_MODELS
from processor import extract_text, generate_quiz_modern
from db import save_quiz_to_db

# --- 1. CSS MODERN (Clean & Animated) ---
def inject_custom_css():
    st.markdown("""
    <style>
        /* Import Font yang bersih (Inter) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Container Card Utama */
        .quiz-container {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 32px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 24px;
            animation: fadeIn 0.5s ease-out;
        }

        /* Dark Mode Support (Basic) */
        @media (prefers-color-scheme: dark) {
            .quiz-container {
                background-color: #1f2937;
                border-color: #374151;
            }
        }

        /* Typography */
        .question-text {
            font-size: 1.25rem;
            font-weight: 600;
            color: #111827;
            margin-bottom: 24px;
        }
        @media (prefers-color-scheme: dark) { .question-text { color: #f3f4f6; } }

        /* Option Card Styling */
        .option-card {
            padding: 16px;
            margin-bottom: 12px;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            transition: all 0.2s ease;
            cursor: default;
        }
        
        /* State Colors */
        .opt-neutral { background-color: transparent; }
        
        .opt-correct { 
            background-color: #ecfdf5; 
            border-color: #10b981; 
            color: #065f46;
        }
        
        .opt-wrong { 
            background-color: #fef2f2; 
            border-color: #ef4444; 
            color: #991b1b;
        }
        
        /* Explanation Box */
        .rationale-text {
            font-size: 0.9rem;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px dashed rgba(0,0,0,0.1);
            opacity: 0.9;
        }

        /* Animation Keyframes */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Hide Streamlit default UI elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stRadio > label {display: none;} /* Sembunyikan label radio default */
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC SHUFFLE ---
def get_shuffled_data(q_index, options_list):
    """
    Mengacak opsi tapi tetap membawa data 'rationale' dan 'is_correct' nya.
    """
    if f"shuffle_{q_index}" not in st.session_state:
        # options_list isinya: [{'text': '...', 'rationale': '...'}, ...]
        # Index 0 adalah benar (dari processor).
        
        # Kita tandai dulu mana yang benar sebelum diacak
        tagged_options = []
        for i, opt in enumerate(options_list):
            opt['is_correct'] = (i == 0) # Tandai True jika index 0
            tagged_options.append(opt)
            
        random.shuffle(tagged_options)
        st.session_state[f"shuffle_{q_index}"] = tagged_options
        
    return st.session_state[f"shuffle_{q_index}"]

# --- 3. UI RENDERER ---
def render_app_modern():
    inject_custom_css()
    
    # Header Simple
    st.markdown("### Quiz Generator")
    st.markdown("---")

    # State Init
    if 'quiz_data' not in st.session_state:
        render_input_section()
    else:
        render_quiz_section()

def render_input_section():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        input_type = st.radio("Input Source", ["Upload File", "Manual Text"], horizontal=True)
        context = ""
        topic = ""
        
        if input_type == "Upload File":
            f = st.file_uploader("Upload Document", type=["pdf", "pptx", "txt"], label_visibility="collapsed")
            if f:
                with st.spinner("Processing..."):
                    context = extract_text(f)
                    topic = f.name
        else:
            context = st.text_area("Paste content here", height=200)
            topic = "Manual Input"

    with col2:
        model_label = st.selectbox("Model", list(AVAILABLE_MODELS.keys()))
        q_count = st.number_input("Question Count", min_value=1, value=10)
        
        st.write("") # Spacer
        if st.button("Generate Quiz", type="primary", use_container_width=True):
            if context:
                with st.spinner("Generating..."):
                    cfg = {"model_id": AVAILABLE_MODELS[model_label], "q_count": q_count}
                    res = generate_quiz_modern(context, cfg)
                    
                    if "error" in res:
                        st.error("Generation failed.")
                    else:
                        # Reset & Save
                        st.session_state.quiz_data = res
                        st.session_state.current_q = 0
                        st.session_state.score = 0
                        st.session_state.user_answers = {} 
                        save_quiz_to_db(topic, "modern_ui", cfg, res)
                        st.rerun()

def render_quiz_section():
    data = st.session_state.quiz_data
    curr = st.session_state.current_q
    total = len(data)
    
    # Progress Bar Tipis
    st.progress((curr + 1) / total)
    
    # Ambil Data Soal
    question_data = data[curr]
    question_text = question_data['question']
    raw_options = question_data['options']
    
    # Acak Opsi
    shuffled_opts = get_shuffled_data(curr, raw_options)
    
    # Container Soal (Putih bersih dengan shadow)
    with st.container():
        st.markdown(f"""
        <div class="quiz-container">
            <div class="question-text">{curr + 1}. {question_text}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # FORM JAWABAN
        # Kita pakai st.radio tapi di-styling biar kayak list group
        display_texts = [opt['text'] for opt in shuffled_opts]
        
        # Cek apakah user sudah jawab soal ini?
        has_answered = f"ans_{curr}" in st.session_state.user_answers
        user_selection = st.session_state.user_answers.get(f"ans_{curr}", None)
        
        if not has_answered:
            # --- MODE BELUM JAWAB ---
            with st.form(key=f"q_form_{curr}"):
                choice = st.radio("Options", display_texts, label_visibility="collapsed")
                submit = st.form_submit_button("Check Answer", use_container_width=True)
                
                if submit:
                    st.session_state.user_answers[f"ans_{curr}"] = choice
                    st.rerun()
        else:
            # --- MODE SUDAH JAWAB (SHOW EXPLANATION CARDS) ---
            
            # 1. Tampilkan setiap opsi sebagai KARTU individual
            for opt in shuffled_opts:
                text = opt['text']
                rationale = opt['rationale']
                is_correct = opt['is_correct']
                is_selected = (text == user_selection)
                
                # Tentukan Style CSS berdasarkan status
                css_class = "opt-neutral"
                status_icon = ""
                
                if is_correct:
                    css_class = "opt-correct"
                    status_icon = "Correct"
                elif is_selected and not is_correct:
                    css_class = "opt-wrong"
                    status_icon = "Your Answer"
                elif not is_selected and not is_correct:
                    # Opsi salah yang tidak dipilih, buat transparan/abu
                    css_class = "option-card" # Default style (grey border)
                
                # Render Kartu HTML
                # Hanya tampilkan penjelasan jika opsi itu BENAR atau DIPILIH SALAH
                show_rationale = is_correct or is_selected
                
                rationale_html = ""
                if show_rationale:
                    rationale_html = f"<div class='rationale-text'><b>Analysis:</b> {rationale}</div>"
                
                # Highlight visual biar jelas mana yang dipilih user
                border_style = "2px solid #000" if is_selected else "1px solid #e5e7eb"
                if is_correct: border_style = "1px solid #10b981"
                if is_selected and not is_correct: border_style = "1px solid #ef4444"

                st.markdown(f"""
                <div class="{css_class} option-card" style="border: {border_style}">
                    <div style="font-weight: 500;">{text}</div>
                    {rationale_html}
                </div>
                """, unsafe_allow_html=True)

            # Tombol Navigasi
            col_nav1, col_nav2 = st.columns([3, 1])
            with col_nav2:
                if curr < total - 1:
                    if st.button("Next Question", type="primary"):
                        st.session_state.current_q += 1
                        st.rerun()
                else:
                    if st.button("Finish Quiz"):
                        st.session_state.quiz_data = None # Reset
                        st.rerun()