import streamlit as st

def render_sidebar():
    """
    Menampilkan sidebar konfigurasi AI dan mengembalikan dictionary config.
    """
    with st.sidebar:
        st.header("🎛️ AI Control Center")
        st.markdown("---")
        
        # --- 1. MODEL SELECTION ---
        st.subheader("1. Otak AI (Model)")
        model = st.selectbox(
            label="Pilih Versi Model",
            options=["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.5-flash-8b"],
            index=1, # Default ke Flash (biar cepet)
            help="Pro = Cerdas/Lambat (Analisis). Flash = Cepat (Hafalan)."
        )
        
        # --- 2. KREATIVITAS (TEMPERATURE) ---
        st.subheader("2. Kreativitas (Temp)")
        temp = st.slider(
            label="Temperature (0.0 - 2.0)",
            min_value=0.0,
            max_value=2.0,
            value=0.3, # Default rendah biar fakta medis akurat
            step=0.1,
            help="0.0 = Robot (Stabil). 1.0 = Manusia (Variatif). 2.0 = Gila (Halusinasi)."
        )
        
        # --- 3. PANJANG JAWABAN (TOKENS) ---
        st.subheader("3. Batas Output (Tokens)")
        max_tok = st.slider(
            label="Max Output Tokens",
            min_value=1000,
            max_value=8192,
            value=4000,
            step=500,
            help="Semakin tinggi, semakin panjang soal/penjelasan yang bisa dibuat."
        )

        st.markdown("---")
        
        # --- 4. SYSTEM PROMPT (Opsional tapi Powerfull) ---
        with st.expander("📝 Instruksi Khusus (System Prompt)", expanded=False):
            default_persona = """You are an Expert Medical Examiner.
Target Audience: Medical Students.
Tone: Strict, Academic, Clinical.
Task: Create high-quality multiple choice questions.
Constraint: Explain WHY the wrong answers are wrong (Pathophysiology)."""
            
            sys_instruct = st.text_area("Persona AI", value=default_persona, height=150)

        # --- INFO VISUAL ---
        st.info(f"Setting Aktif:\nModel: {model}\nTemp: {temp}\nTokens: {max_tok}")
        
        # Kembalikan semua settingan ini sebagai Dictionary ke main.py
        return {
            "model": model,
            "temp": temp,
            "max_tokens": max_tok,
            "system_instruction": sys_instruct,
            # Kita set default top_p agar aman
            "top_p": 0.95
        }