"""
✍️ مُشكِّل النصوص العربية — نقطة البداية
=============================================

هذا هو الملف الرئيسي الذي يشغّل تطبيق Streamlit.
يستورد جميع المكونات من الوحدات الفرعية ويجمعها معاً.

التشغيل:
    streamlit run app_streamlit.py
"""

import streamlit as st
import logging

# ── إعداد السجلات ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ══════════════════════════════════════════════════════
#          1. إعدادات الصفحة (يجب أن تكون أولاً)
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="مُشكِّل النصوص العربية | CATT",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════
#          2. الاستيرادات (بعد set_page_config)
# ══════════════════════════════════════════════════════
from core.engine import ArabicDiacritizer
from core.samples import SAMPLE_CATEGORIES

from ui.styles import inject_styles
from ui.sidebar import render_sidebar
from ui.tab_tashkeel import render_tab_tashkeel
from ui.tab_file import render_tab_file
from ui.tab_info import render_tab_info

# ══════════════════════════════════════════════════════
#          3. حقن أنماط CSS
# ══════════════════════════════════════════════════════
inject_styles()

# ══════════════════════════════════════════════════════
#          4. تحميل النموذج (مرة واحدة)
# ══════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def load_model(fast_mode: bool = True):
    """تحميل النموذج وتخزينه مؤقتاً"""
    return ArabicDiacritizer(fast_mode=fast_mode)


# ══════════════════════════════════════════════════════
#          5. الشريط الجانبي
# ══════════════════════════════════════════════════════
fast_mode, selected_sample, strip_mode = render_sidebar(
    SAMPLE_CATEGORIES
)

# تحديث الإدخال إذا ضُغط نموذج جاهز
if selected_sample is not None:
    st.session_state["input_text"] = selected_sample

# ══════════════════════════════════════════════════════
#          6. الهيدر الرئيسي
# ══════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <span class="hero-icon">✍️</span>
    <h1>مُشكِّل النصوص العربية</h1>
    <p>تشكيل آلي ذكي باستخدام نموذج CATT للذكاء الاصطناعي</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#          7. تحميل النموذج وعرض الحالة
# ══════════════════════════════════════════════════════
with st.spinner("🔄 جاري تحميل النموذج... قد يستغرق دقيقة"):
    diacritizer = load_model(fast_mode=fast_mode)

MODEL_OK = diacritizer.is_loaded
IS_DEMO = not MODEL_OK

if MODEL_OK:
    st.markdown(
        f'<div class="badge badge-ok">'
        f"✅ النموذج جاهز &nbsp;|&nbsp; {diacritizer.model_type}"
        f"</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="badge badge-demo">'
        "⚡ وضع العرض التجريبي — نماذج مُشكّلة مسبقاً"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.expander(
        "🔍 لماذا لم يُحمّل النموذج؟ (اضغط للتفاصيل)"
    ):
        st.error(f"**السبب:**\n\n{diacritizer.load_error}")
        st.markdown(
            "### 🛠️ الحل:\n\n"
            "**1. تأكد من ملف `requirements.txt`:**\n"
            "```\n"
            "--extra-index-url "
            "https://download.pytorch.org/whl/cpu\n"
            "torch\n"
            "transformers\n"
            "sentencepiece\n"
            "protobuf\n"
            "catt-tashkeel\n"
            "streamlit\n"
            "```\n\n"
            "**2. أضف ملف `packages.txt`:**\n"
            "```\n"
            "build-essential\n"
            "libsndfile1\n"
            "```\n\n"
            "**3. أو شغّل محلياً:**\n"
            "```bash\n"
            "pip install catt-tashkeel streamlit\n"
            "streamlit run app_streamlit.py\n"
            "```"
        )

    st.markdown(
        '<div class="demo-notice">'
        "💡 جرّب النماذج الجاهزة من الشريط الجانبي. "
        "لتشكيل أي نص حر، شغّل التطبيق محلياً."
        "</div>",
        unsafe_allow_html=True,
    )

st.markdown("")

# ══════════════════════════════════════════════════════
#          8. التبويبات الثلاثة
# ══════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(
    ["✍️ تشكيل فوري", "📄 معالجة ملف", "ℹ️ معلومات"]
)

with tab1:
    render_tab_tashkeel(diacritizer, IS_DEMO, strip_mode)

with tab2:
    render_tab_file(diacritizer, IS_DEMO)

with tab3:
    render_tab_info(diacritizer, MODEL_OK)

# ══════════════════════════════════════════════════════
#          9. الفوتر
# ══════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div class="app-footer">
    <p>
        ✍️ <strong>مُشكِّل النصوص العربية</strong>
        &nbsp;|&nbsp; نموذج CATT للذكاء الاصطناعي
    </p>
    <p style="margin-top:0.3rem;">
        صُنع بـ ❤️ للغة العربية &nbsp;|&nbsp;
        <a href="https://github.com/GT-SALT/CATT"
           target="_blank">GitHub</a>
    </p>
</div>
""", unsafe_allow_html=True)
