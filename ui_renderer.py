import streamlit as st
import json

def render_custom_css():
    """Inject CSS biar tampilan lebih Pro/Medical."""
    st.markdown("""
    <style>
        .stExpander { border: 1px solid #e0e0e0; border-radius: 8px; }
        .stButton button { border-radius: 20px; }
        .success-box { padding: 10px; background-color: #d4edda; color: #155724; border-radius: 5px; border-left: 5px solid #28a745; }
        .warning-box { padding: 10px; background-color: #fff3cd; color: #856404; border-radius: 5px; border-left: 5px solid #ffc107; }
    </style>
    """, unsafe_allow_html=True)

def render_quiz_result(data, topic_name):
    """Menampilkan hasil kuis dalam bentuk kartu interaktif."""
    
    st.success(f"✅ Generated: {topic_name}")
    
    # Validasi Data
    if not isinstance(data, list):
        st.error("Format data rusak (Bukan List). Cek Raw JSON tab.")
        return

    # Progress Bar visual
    total = len(data)
    st.progress(100, text=f"Total {total} Soal Siap.")

    for i, q in enumerate(data):
        # Gunakan Expander untuk setiap soal biar rapi
        question_text = q.get('question', 'No Question')
        with st.expander(f"Q{i+1}: {question_text[:60]}...", expanded=False):
            st.markdown(f"### {question_text}")
            st.divider()
            
            # Tampilkan Opsi
            opts = q.get('options', [])
            correct = q.get('answer')
            explanation = q.get('explanation')
            
            # Kolom untuk opsi (biar gak panjang ke bawah)
            col1, col2 = st.columns(2)
            for idx, opt in enumerate(opts):
                # Ganti kolom kiri/kanan bergantian
                target_col = col1 if idx % 2 == 0 else col2
                
                # Logic Warna (Hanya untuk preview developer/belajar)
                if opt == correct:
                    target_col.markdown(f"<div class='success-box'>✅ {opt}</div>", unsafe_allow_html=True)
                else:
                    target_col.markdown(f"<div class='warning-box'>⚪ {opt}</div>", unsafe_allow_html=True)
                
                target_col.write("") # Spacer

            st.write("---")
            st.info(f"💡 **Rationale:** {explanation}")

def render_raw_json(data):
    """Menampilkan JSON mentah untuk debug atau copy-paste."""
    st.caption("Salin kode ini jika ingin dimasukkan ke aplikasi lain.")
    st.code(json.dumps(data, indent=2), language="json")