def get_modern_css():
    return """
    <style>
        /* 1. RESET & BASIC LAYOUT */
        .stApp {
            background-color: #0f1116; /* Deep Dark Background */
        }
        
        /* Hapus padding atas default Streamlit biar kaya App */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 5rem;
            max-width: 700px; /* Batasi lebar biar fokus seperti Mobile View */
        }

        /* 2. ANIMASI (Movement) */
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-card {
            animation: slideIn 0.4s ease-out forwards;
        }

        /* 3. QUESTION CARD */
        .question-card {
            background-color: #1e232e;
            padding: 24px;
            border-radius: 16px;
            border: 1px solid #2d3342;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        
        .question-text {
            font-size: 1.3rem;
            font-weight: 600;
            color: #ffffff;
            line-height: 1.5;
        }
        
        .question-meta {
            font-size: 0.85rem;
            color: #8b949e;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* 4. RESULT CARDS (Pemisahan Analisis) */
        .result-container {
            margin-top: 20px;
            animation: slideIn 0.5s ease-out forwards;
        }

        .status-card-correct {
            background-color: rgba(35, 134, 54, 0.15);
            border: 1px solid #238636;
            color: #46c45b;
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 12px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status-card-wrong {
            background-color: rgba(218, 54, 51, 0.15);
            border: 1px solid #da3633;
            color: #f85149;
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 12px;
            font-weight: bold;
        }

        .explanation-card {
            background-color: #262c36;
            border-left: 4px solid #58a6ff; /* Accent Blue */
            padding: 20px;
            border-radius: 8px;
            color: #d0d7de;
            line-height: 1.6;
            font-size: 0.95rem;
        }

        /* 5. STYLING RADIO BUTTON BIAR JADI CARD */
        /* Kita manipulasi elemen internal Streamlit */
        div[role="radiogroup"] > label {
            background-color: #161b22;
            padding: 16px;
            border-radius: 10px;
            border: 1px solid #30363d;
            margin-bottom: 10px;
            transition: all 0.2s;
            cursor: pointer;
        }

        div[role="radiogroup"] > label:hover {
            background-color: #21262d;
            border-color: #8b949e;
            transform: translateX(5px); /* Micro interaction pas hover */
        }
        
        /* Hilangkan lingkaran radio default (opsional, tergantung preferensi) */
        div[role="radiogroup"] label > div:first-child {
            display: none; 
        }

        /* Tambahkan efek 'selected' visual lewat CSS agak tricky di st, 
           jadi kita andalkan feedback visual UI logic */

    </style>
    """
