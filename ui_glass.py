import streamlit as st
import random
from style import get_glass_css
from config import AVAILABLE_MODELS
from processor import extract_text, generate_quiz_dynamic
from db import save_quiz_to_db

# --- INITIALIZE SESSION STATE (Penting buat Game Loop) ---
def init_game_state():
    if 'current_idx' not in st.session_state:
        st.session_state.current_idx = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {} # {soal_index: 'jawaban_user'}
    if 'shuffled_maps' not in st.session_state:
        st.session_state.shuffled_maps = {} # Nyimpen kunci jawaban yang udah diacak

# --- FUNGSI PENGACAK OPSI ---
def get_shuffled_options(question_index, original_options):
    """
    Menerima list opsi mentah [Benar, Salah1, Salah2, Salah3]
    Mengembalikan list tuple yang diacak [(Salah1, 1), (Benar, 0), ...]
    Index 0 selalu Jawaban Benar (karena logic processor kita).
    """
    # Cek apakah soal ini sudah pernah diacak sebelumnya? (Biar gak berubah pas reload)
    if question_index in st.session_state.shuffled_maps:
        return st.session_state.shuffled_maps[question_index]
    
    # Kalau belum, kita acak sekarang
    # Kita pasangkan teks opsi dengan index aslinya: [(0, "Jawaban Benar"), (1, "Salah A"), ...]
    indexed_options = list(enumerate(original_options))
    
    # ACAK!
    random.shuffle(indexed_options)
    
    # Simpan ke session state biar konsisten
    st.session_state.shuffled_maps[question_index] = indexed_options
    return indexed_options

# --- UI RENDERER UTAMA ---
def render_app_glass():
    # 1. Inject CSS Glass
    st.markdown(get_glass_css(), unsafe_allow_html=True)
    init_game_state()

    st.title("💎 Glass Quiz: Focus Mode")

    # --- LAYOUT INPUT vs GAME ---
    # Kalau belum ada quiz data, tampilkan menu INPUT
    if 'quiz_data' not in st.session_state:
        render_input_menu()
    else:
        # Kalau sudah ada data, masuk ke GAME MODE
        render_game_play()

def render_input_menu():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<div class='glass-card'><h3>📥 Upload Material</h3>", unsafe_allow_html=True)
        input_type = st.radio("Source", ["File", "Text"], label_visibility="collapsed")
        
        context = ""
        topic = ""
        
        if input_type == "File":
            f = st.file_uploader("PDF/PPT/TXT", label_visibility="collapsed")
            if f:
                context = extract_text(f)
                topic = f.name
                st.success(f"Loaded: {len(context)} chars")
        else:
            context = st.text_area("Paste Text Here", height=150)
            topic = "Manual Input"
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'><h3>⚙️ Engine Config</h3>", unsafe_allow_html=True)
        model_key = st.selectbox("Model", list(AVAILABLE_MODELS.keys()))
        q_count = st.number_input("Soal", 5, 100, 10)
        mode = st.selectbox("Mode", ["Guided", "Case", "Drill"])
        
        if st.button("🔥 IGNITE", type="primary", use_container_width=True):
            if context:
                with st.spinner("Generating..."):
                    cfg = {"model_id": AVAILABLE_MODELS[model_key], "q_count": q_count, "mode": mode}
                    res = generate_quiz_dynamic(context, cfg)
                    
                    if "error" in res:
                        st.error("Error")
                    else:
                        st.session_state.quiz_data = res
                        st.session_state.quiz_meta = f"{topic}"
                        # Reset State Game
                        st.session_state.current_idx = 0
                        st.session_state.score = 0
                        st.session_state.shuffled_maps = {}
                        save_quiz_to_db(topic, "glass_mode", cfg, res)
                        st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def render_game_play():
    # Ambil Data
    quiz_list = st.session_state.quiz_data
    curr = st.session_state.current_idx
    total = len(quiz_list)
    
    # Progress Bar di atas
    progress = (curr + 1) / total
    st.progress(progress, text=f"Question {curr + 1} of {total}")
    
    # Ambil Soal Saat Ini
    q_data = quiz_list[curr]
    question_text = q_data.get('question')
    original_options = q_data.get('options') # Index 0 pasti benar (dari processor)
    explanation = q_data.get('explanation')
    
    # Logic Pengacak (Shuffle)
    # shuffled_opts isinya list tuple: [(IndexAsli, TeksOpsi), ...]
    shuffled_opts = get_shuffled_options(curr, original_options)
    
    # Pisahkan untuk display di Radio Button
    display_options = [opt_text for (idx, opt_text) in shuffled_opts]
    
    # --- GLASS CARD PERTANYAAN ---
    st.markdown(f"""
    <div class='glass-card'>
        <h3>{question_text}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # --- AREA JAWABAN ---
    # Kita pakai form biar gak reload tiap klik radio button
    with st.form(key=f"form_{curr}"):
        user_choice_text = st.radio("Pilih Jawaban:", display_options, index=None, label_visibility="collapsed")
        
        # Tombol Submit (Cek Jawaban)
        submitted = st.form_submit_button("🔒 Kunci Jawaban", use_container_width=True)
    
    # --- ASSESMENT LOGIC (TANPA AI) ---
    if submitted and user_choice_text:
        # Cari Index Asli dari pilihan user
        # Kita looping shuffled_opts untuk cari mana tuple yang text-nya sama dengan pilihan user
        selected_original_index = -1
        for (idx, txt) in shuffled_opts:
            if txt == user_choice_text:
                selected_original_index = idx
                break
        
        # LOGIC INTI: Apakah Index Asli == 0? (Karena AI selalu taruh jawaban benar di 0)
        is_correct = (selected_original_index == 0)
        
        if is_correct:
            st.markdown(f"""
            <div class='feedback-correct'>
                <b>✅ BENAR SEKALI!</b><br>
                {user_choice_text} adalah jawaban yang tepat.
            </div>
            """, unsafe_allow_html=True)
            st.balloons() # Efek visual
        else:
            # Cari teks jawaban yang benar (Index 0)
            correct_text = original_options[0]
            st.markdown(f"""
            <div class='feedback-wrong'>
                <b>❌ KURANG TEPAT.</b><br>
                Jawaban Anda: {user_choice_text}<br>
                <b>Jawaban Benar: {correct_text}</b>
            </div>
            """, unsafe_allow_html=True)

        # Tampilkan Penjelasan (Glass Box juga)
        st.markdown(f"""
        <div class='glass-card' style='margin-top: 20px; background: rgba(0,0,0,0.3);'>
            <h4>📚 Analisis & Penjelasan</h4>
            <p>{explanation}</p>
        </div>
        """, unsafe_allow_html=True)

        # Tombol Next (Di luar form biar logic flow jalan)
        # Hacky way: Gunakan button di luar form untuk increment state
        st.session_state[f"answered_{curr}"] = True

    # Tombol Next Navigasi
    col_nav1, col_nav2 = st.columns([4, 1])
    with col_nav2:
        if st.session_state.get(f"answered_{curr}"):
            if curr < total - 1:
                if st.button("Next ➡️"):
                    st.session_state.current_idx += 1
                    st.rerun()
            else:
                if st.button("Finish 🏁"):
                    st.success("Quiz Selesai! Refresh untuk mulai baru.")
                    # Bisa tambah logic save score ke DB disini