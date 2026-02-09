import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Load Kunci Rahasia dari .env
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# 2. Validasi Koneksi (Biar gak error diam-diam)
if not url or not key:
    raise ValueError("ERROR: Supabase URL/KEY belum diset di .env!")

supabase: Client = create_client(url, key)

# 3. Fungsi Simpan Kuis
def save_quiz_to_db(topic, source_type, settings, content):
    """
    Menyimpan hasil generate Gemini ke tabel 'quizzes'.
    """
    data = {
        "topic_or_filename": topic,  # Nama file atau topik manual
        "source_type": source_type,  # 'file' atau 'topic'
        "settings": settings,        # Dict: {'model': '...', 'difficulty': '...'}
        "quiz_content": content      # JSON hasil generate Gemini
    }
    
    # Eksekusi Insert
    try:
        response = supabase.table("quizzes").insert(data).execute()
        return response
    except Exception as e:
        print(f"Database Error: {e}")
        return None

# 4. Fungsi Ambil History (Buat Sidebar nanti)
def get_recent_quizzes(limit=5):
    """
    Mengambil 5 kuis terakhir yang pernah dibuat.
    """
    try:
        response = supabase.table("quizzes")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return response.data
    except Exception as e:
        print(f"Fetch Error: {e}")
        return []