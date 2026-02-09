# config.py

# Daftar Model yang tersedia. 
# Format: "Label yang Tampil di UI": "ID Model API"
AVAILABLE_MODELS = {
    "Gemma 3 (27B) - Experimental Cepat": "gemma-3-27b-it",
    "Gemini 3 Flash - Paling Pintar (Context Besar)": "gemini-3-flash-preview",
    "Gemini 2.5 Flash - Standard & Stabil": "gemini-2.5-flash",
    "Gemini 2.5 Flash Lite - Versi Ringan": "gemini-2.5-flash-lite",
    "Gemini 2.5 Pro - Advanced Reasoning": "gemini-2.5-pro"
}

# Default Prompt Template (Bisa lo edit sesuka hati tanpa nyentuh processor)
DEFAULT_SYSTEM_PROMPT = """
ROLE: Expert Medical & Academic Examiner.
TASK: Create a Multiple Choice Quiz.
LANGUAGE: Indonesian (Formal).

CRITICAL RULES:
1. Output MUST be a raw JSON Array.
2. Analyze EVERY OPTION in the explanation (Why A is correct, Why B/C/D is wrong).
3. Do not be lazy.
"""