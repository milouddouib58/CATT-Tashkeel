"""
مُشكِّل النصوص العربية - CATT Tashkeel
نقطة البداية الرئيسية للتطبيق
"""

import streamlit as st
import logging
import sys
import os

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ══════════════════════════════════════════
#    إعدادات الصفحة - يجب أن تكون أولاً
# ══════════════════════════════════════════
st.set_page_config(
    page_title="مُشكِّل النصوص العربية",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════
#    الاستيرادات
# ══════════════════════════════════════════
try:
    from core.engine import ArabicDiacritizer
    from core.samples import SAMPLE_CATEGORIES
    from helpers import do_tashkeel, check_dependencies
    from ui.styles import inject_styles
    from ui.sidebar import render_sidebar
    from ui.tab_tashkeel import render_tab_tashkeel
    from ui.tab_file import render_tab_file
    from ui.tab_info import render_tab_info

    IMPORTS_OK = True
    IMPORT_ERROR = ""
except ImportError as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)

# ══════════════════════════════════════════
#    التطبيق الرئيسي
# ══════════════════════════════════════════
def main():
    """الدالة الرئيسية للتطبيق"""

    if not IMPORTS_OK:
        st.error(
            f"❌ خطأ في استيراد الملفات:\n\n"
            f"`{IMPORT_ERROR}`\n\n"
            f"تأكد من وجود جميع الملفات في المستودع."
        )
        st.markdown("### الملفات المطلوبة:")
        st.code(
            "core/__init__.py\n"
            "core/engine.py\n"
            "core/samples.py\n"
            "ui/__init__.py\n"
            "ui/styles.py\n"
            "ui/sidebar.py\n"
            "ui/tab_tashkeel.py\n"
            "ui/tab_file.py\n"
            "ui/tab_info.py\n"
            "helpers.py",
            language=None,
        )
        st.stop()

    # حقن CSS
    inject_styles()

    # الشريط الجانبي
    fast_mode, selected_sample, strip_mode = render_sidebar(
        SAMPLE_CATEGORIES
    )

    if selected_sample is not None:
        st.session_state["input_text"] = selected_sample

    # الهيدر
    st.markdown(
        '<div class="hero">'
        '<span class="hero-icon">✍️</span>'
        "<h1>مُشكِّل النصوص العربية</h1>"
        "<p>تشكيل آلي ذكي باستخدام نموذج CATT</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # تحميل النموذج
    diacritizer = load_model(fast_mode)

    model_ok = diacritizer.is_loaded
    is_demo = not model_ok

    # عرض حالة النموذج
    if model_ok:
        st.markdown(
            f'<div class="badge badge-ok">'
            f"✅ النموذج جاهز | {diacritizer.model_type}"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="badge badge-demo">'
            "⚡ وضع تجريبي — نماذج مُشكّلة مسبقاً"
            "</div>",
            unsafe_allow_html=True,
        )
        _show_error_details(diacritizer.load_error)

    st.markdown("")

    # التبويبات
    tab1, tab2, tab3 = st.tabs(
        ["✍️ تشكيل فوري", "📄 معالجة ملف", "ℹ️ معلومات"]
    )

    with tab1:
        render_tab_tashkeel(diacritizer, is_demo, strip_mode)

    with tab2:
        render_tab_file(diacritizer, is_demo)

    with tab3:
        render_tab_info(diacritizer, model_ok)

    # الفوتر
    st.markdown("---")
    st.markdown(
        '<div class="app-footer">'
        "<p>✍️ <strong>مُشكِّل النصوص العربية</strong>"
        " | نموذج CATT</p>"
        "<p>صُنع بـ ❤️ للغة العربية</p>"
        "</div>",
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def load_model(fast_mode):
    """تحميل النموذج مرة واحدة"""
    with st.spinner("🔄 جاري تحميل النموذج..."):
        return ArabicDiacritizer(fast_mode=fast_mode)


def _show_error_details(error_msg):
    """عرض تفاصيل الخطأ"""
    with st.expander("🔍 التفاصيل"):
        st.error(f"**السبب:**\n\n{error_msg}")
        st.markdown(
            "**الحل:** شغّل التطبيق محلياً:\n"
            "```bash\n"
            "pip install catt-tashkeel streamlit\n"
            "streamlit run app_streamlit.py\n"
            "```"
        )

    st.markdown(
        '<div class="demo-notice">'
        "💡 جرّب النماذج الجاهزة من الشريط الجانبي"
        "</div>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════
#    التشغيل
# ══════════════════════════════════════════
if __name__ == "__main__":
    main()
else:
    main()
