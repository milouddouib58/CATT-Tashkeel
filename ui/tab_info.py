"""تبويب المعلومات"""

import sys
import streamlit as st
from helpers import check_dependencies
from core.samples import DEMO_PAIRS


def render_tab_info(diacritizer, is_model_ok):
    """عرض تبويب المعلومات"""

    st.markdown("### ℹ️ حول المشروع")
    st.markdown(
        "**مُشكِّل النصوص العربية** يستخدم نموذج "
        "**CATT** للتعلم العميق لإضافة الحركات تلقائياً.\n\n"
        "---\n"
        "#### 🚀 التشغيل المحلي\n"
        "```bash\n"
        "pip install catt-tashkeel streamlit\n"
        "streamlit run app_streamlit.py\n"
        "```"
    )

    st.markdown("---")
    st.markdown("#### 🖥️ حالة النظام")

    deps = check_dependencies()
    tbl = '<table class="diag-tbl">'
    tbl += "<tr><th>المكتبة</th><th>الحالة</th><th>الإصدار</th></tr>"
    for lib, info in deps.items():
        if info["installed"]:
            tbl += f'<tr><td>{lib}</td><td class="clr-ok">✅</td><td>{info["version"]}</td></tr>'
        else:
            tbl += f'<tr><td>{lib}</td><td class="clr-fail">❌</td><td>—</td></tr>'
    tbl += "</table>"
    st.markdown(tbl, unsafe_allow_html=True)

    status = f"✅ {diacritizer.model_type}" if is_model_ok else "❌ تجريبي"
    st.markdown(f"- **Python:** `{sys.version_info.major}.{sys.version_info.minor}`")
    st.markdown(f"- **النموذج:** {status}")

    if not is_model_ok:
        st.markdown("---")
        st.markdown("#### 📝 النماذج المتوفرة")
        for orig, dia in DEMO_PAIRS.items():
            with st.expander(orig[:40]):
                st.markdown(f"_{dia}_")
