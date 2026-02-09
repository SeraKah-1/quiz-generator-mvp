import streamlit as st
from config import AVAILABLE_MODELS
from processor import extract_text, generate_quiz_dynamic
from db import save_quiz_to_db

def render_results(data, meta_info):
    """Fungsi khusus buat nampilin soal biar rapi"""
    st.divider()
    st.subheader(f"📝 Hasil: {meta_info}")
    
    if isinstance(data, list):
        for i, q in enumerate(data):
            # Pakai Container biar terkotak rapi
            with st.container(border=True):
                # Header Soal
                st.markdown(f"#### {i+1}. {q.get('question', 'No Question Text')}")
                
                opts = q.get('options', [])
                correct = q.get('answer', "")
                expl = q.get('explanation', "")
                
                # Radio Button (Jawaban User)
                # Key unik per soal biar gak bentrok
                user_ans = st.radio(
                    "Pilih Jawaban:", 
                    opts, 
                    key=f"q_{i}", 
                    index=None, 
                    label_visibility="collapsed"
                )
                
                # Logic Reveal (Langsung kasih tau bener/salah & penjelasan)
                if user_ans:
                    if user_ans == correct:
                        st.success(f"✅ Benar! {user_ans}")
                    else:
                        st.error(f"❌ Salah. Jawaban yang benar: {correct}")
                    
                    # Penjelasan (Expandable)
                    with st.expander("📖 Lihat Analisis & Penjelasan", expanded=True):
                        st.info(expl)
    else:
        st.error("Format JSON dari AI rusak. Coba generate ulang atau ganti model.")
        with st.expander("Debug Raw Data"):
            st.json(data)

def render_app():
    """Fungsi Utama UI"""
    st.title("💀 Quiz Generator: Modular UI")
    
    # --- LAYOUT 2 KOLOM (INPUT vs CONFIG) ---
    col_left, col_right = st.columns([1, 1], gap="medium")
    
    # Variabel penampung
    context_text = ""
    topic_name = ""

    # === KOLOM KIRI: INPUT ===
    with col_left:
        st.subheader("1. Sumber Materi")
        tab1, tab2 = st.tabs(["📁 Upload File", "✍️ Paste Text"])
        
        with tab1:
            f = st.file_uploader("Upload PDF/PPT/TXT", type=["pdf", "pptx", "md", "txt"])
            if f:
                topic_name = f.name
                with st.spinner("Membaca file..."):
                    context_text = extract_text(f)
                st.success(f"Terbaca: {len(context_text)} karakter")
        
        with tab2:
            txt_in = st.text_area("Paste materi disini...", height=200)
            if txt_in:
                topic_name = "Manual Input"
                context_text = txt_in

    # === KOLOM KANAN: CONFIG ===
    with col_right:
        st.subheader("2. Konfigurasi Mesin")
        
        # A. Model Selector (Dinamis dari config.py)
        model_label = st.selectbox("Pilih Model AI", list(AVAILABLE_MODELS.keys()))
        selected_model_id = AVAILABLE_MODELS[model_label]
        
        # B. Jumlah Soal (Freedom Input)
        q_count = st.number_input("Target Jumlah Soal", min_value=1, value=10, step=1)
        
        # C. Mode Belajar
        mode_select = st.selectbox(
            "Mode Belajar", 
            ["Guided Learning (Bertingkat)", "Clinical Case (Kasus)", "Freedom Review (Acak)", "Hardcore Drill (Jebakan)"]
        )
        
        st.write("") # Spacer
        
        # TOMBOL EKSEKUSI
        if st.button("🔥 GENERATE QUIZ", type="primary", use_container_width=True):
            if not context_text:
                st.toast("❌ Materi kosong bos!", icon="⚠️")
            else:
                # Bungkus Config
                run_config = {
                    "model_id": selected_model_id,
                    "q_count": q_count,
                    "mode": mode_select
                }
                
                with st.spinner(f"Sedang meracik soal dengan {model_label}..."):
                    # Panggil Processor (Backend)
                    result = generate_quiz_dynamic(context_text, run_config)
                    
                    if "error" in result:
                        st.error("Terjadi Kesalahan:")
                        st.code(result)
                    else:
                        # Simpan ke Session State & DB
                        st.session_state['quiz_data'] = result
                        st.session_state['quiz_meta'] = f"{topic_name} | {mode_select}"
                        save_quiz_to_db(topic_name, "modular_ui", run_config, result)
                        st.toast("Berhasil! Scroll ke bawah.", icon="✅")

    # === BAGIAN BAWAH: HASIL ===
    if 'quiz_data' in st.session_state:
        render_results(st.session_state['quiz_data'], st.session_state['quiz_meta'])
