# style.py

def get_glass_css():
    return """
    <style>
    /* Background Global (Dark Gradient biar Glass Kelihatan) */
    .stApp {
        background-color: #0e1117;
        background-image: radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
                          radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
                          radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
    }

    /* GLASS CARD CONTAINER */
    .glass-card {
        background: rgba(255, 255, 255, 0.05); /* Transparan */
        backdrop-filter: blur(10px);           /* Efek Blur/Frosted */
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1); /* Border tipis */
        border-radius: 16px;
        padding: 30px;
        margin-bottom: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        color: white;
    }

    /* Typography */
    .glass-card h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 20px;
    }

    /* FEEDBACK BOXES */
    .feedback-correct {
        background: rgba(46, 204, 113, 0.2);
        border-left: 4px solid #2ecc71;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
        backdrop-filter: blur(5px);
    }
    
    .feedback-wrong {
        background: rgba(231, 76, 60, 0.2);
        border-left: 4px solid #e74c3c;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
        backdrop-filter: blur(5px);
    }

    /* Custom Radio Button Styling (Agak tricky di Streamlit) */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """