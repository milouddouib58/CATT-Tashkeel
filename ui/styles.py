"""
أنماط CSS المخصصة للتطبيق
تصميم داكن عصري مع لمسات ذهبية

نظام الألوان:
    - الذهبي (#e9c46a): العناوين والعناصر الرئيسية
    - السماوي (#a8dadc): النصوص الثانوية
    - البرتقالي (#f4a261): التدرجات
    - الداكن (#0a0a1a → #0f3460): الخلفيات
"""

import streamlit as st


def inject_styles():
    """حقن أنماط CSS في الصفحة"""
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = """
<style>
    /* ══════════════════════════════════
              الخطوط العربية
       ══════════════════════════════════ */
    @import url(
        'https://fonts.googleapis.com/css2?'
        'family=Tajawal:wght@300;400;500;700;900'
        '&display=swap'
    );
    @import url(
        'https://fonts.googleapis.com/css2?'
        'family=Amiri:wght@400;700'
        '&display=swap'
    );

    * {
        font-family: 'Tajawal', sans-serif !important;
    }

    .main .block-container {
        padding-top: 1.5rem;
        max-width: 1200px;
    }

    /* ══════════════════════════════════
              الهيدر الرئيسي
       ══════════════════════════════════ */
    .hero {
        background: linear-gradient(
            135deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%
        );
        padding: 2.5rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.4);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(233,196,106,0.15);
    }

    .hero::before {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(
            ellipse at 30% 50%,
            rgba(233,196,106,0.06) 0%,
            transparent 60%
        );
        pointer-events: none;
    }

    .hero-icon {
        font-size: 3rem;
        display: block;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }

    .hero h1 {
        color: #e9c46a !important;
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        margin: 0 !important;
        position: relative;
        z-index: 1;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.4);
    }

    .hero p {
        color: #a8dadc !important;
        font-size: 1.1rem !important;
        margin-top: 0.5rem !important;
        position: relative;
        z-index: 1;
        font-weight: 300;
    }

    /* ══════════════════════════════════
              مربعات النص
       ══════════════════════════════════ */
    .stTextArea textarea {
        font-family: 'Amiri', serif !important;
        font-size: 1.35rem !important;
        line-height: 2.2 !important;
        direction: rtl !important;
        text-align: right !important;
        border: 2px solid rgba(233,196,106,0.2) !important;
        border-radius: 15px !important;
        padding: 1.2rem !important;
        background: rgba(26,26,46,0.5) !important;
        color: #e0e0e0 !important;
        transition: all 0.3s ease !important;
    }

    .stTextArea textarea:focus {
        border-color: #e9c46a !important;
        box-shadow: 0 0 0 3px rgba(233,196,106,0.15) !important;
        background: rgba(26,26,46,0.8) !important;
    }

    .stTextArea textarea::placeholder {
        color: rgba(255,255,255,0.3) !important;
    }

    /* ══════════════════════════════════
              مربع النتيجة
       ══════════════════════════════════ */
    .result-box {
        background: linear-gradient(
            135deg,
            rgba(233,196,106,0.08),
            rgba(244,162,97,0.05)
        );
        border: 2px solid rgba(233,196,106,0.3);
        border-radius: 15px;
        padding: 1.8rem;
        direction: rtl;
        text-align: right;
        font-family: 'Amiri', serif !important;
        font-size: 1.5rem;
        line-height: 2.5;
        color: #e9c46a;
        min-height: 180px;
        box-shadow: 0 4px 20px rgba(233,196,106,0.08);
        word-wrap: break-word;
    }

    .result-box-empty {
        color: rgba(255,255,255,0.25) !important;
        font-family: 'Tajawal', sans-serif !important;
        font-size: 1rem !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* ══════════════════════════════════
              بطاقات الإحصائيات
       ══════════════════════════════════ */
    .metric-card {
        background: linear-gradient(135deg, #16213e, #1a1a2e);
        border-radius: 15px;
        padding: 1.3rem;
        text-align: center;
        border: 1px solid rgba(233,196,106,0.15);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(233,196,106,0.35);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }

    .metric-val {
        font-size: 2rem;
        font-weight: 900;
        color: #e9c46a;
        display: block;
    }

    .metric-lbl {
        font-size: 0.9rem;
        color: #a8dadc;
        margin-top: 0.2rem;
        display: block;
    }

    /* ══════════════════════════════════
              شارات الحالة
       ══════════════════════════════════ */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1.2rem;
        border-radius: 50px;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    .badge-ok {
        background: rgba(46,204,113,0.12);
        border: 1px solid rgba(46,204,113,0.3);
        color: #2ecc71;
    }

    .badge-demo {
        background: rgba(243,156,18,0.12);
        border: 1px solid rgba(243,156,18,0.3);
        color: #f39c12;
    }

    .demo-notice {
        background: rgba(243,156,18,0.1);
        border: 1px solid rgba(243,156,18,0.25);
        color: #f39c12;
        padding: 0.8rem 1.2rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem 0;
        font-size: 0.95rem;
        direction: rtl;
    }

    /* ══════════════════════════════════
              الأزرار
       ══════════════════════════════════ */
    .stButton > button {
        width: 100%;
        padding: 0.85rem 1.5rem !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }

    /* ══════════════════════════════════
              الشريط الجانبي
       ══════════════════════════════════ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg, #1a1a2e 0%, #16213e 100%
        ) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #e0e0e0 !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #e9c46a !important;
    }

    /* ══════════════════════════════════
              جدول التشخيص
       ══════════════════════════════════ */
    .diag-tbl {
        width: 100%;
        border-collapse: collapse;
        direction: rtl;
        margin: 0.5rem 0;
    }

    .diag-tbl th, .diag-tbl td {
        padding: 0.5rem 0.8rem;
        text-align: right;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        font-size: 0.9rem;
    }

    .diag-tbl th {
        color: #e9c46a;
        font-weight: 700;
    }

    .clr-ok   { color: #2ecc71; }
    .clr-fail { color: #e74c3c; }

    /* ══════════════════════════════════
              الفوتر
       ══════════════════════════════════ */
    .app-footer {
        text-align: center;
        padding: 2rem 1rem;
        color: #555;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 3rem;
        font-size: 0.9rem;
    }

    .app-footer a {
        color: #e9c46a;
        text-decoration: none;
    }

    .app-footer a:hover {
        text-decoration: underline;
    }

    /* ══════════════════════════════════
              إخفاء عناصر Streamlit
       ══════════════════════════════════ */
    #MainMenu  { visibility: hidden; }
    footer     { visibility: hidden; }
    header     { visibility: hidden; }
</style>
"""
