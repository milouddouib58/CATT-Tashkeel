"""الشريط الجانبي"""

import sys
import streamlit as st
from helpers import check_dependencies


def render_sidebar(sample_categories):
    """عرض الشريط الجانبي"""
    selected_sample = None

    with st.sidebar:
        st.markdown("## ⚙️ الإعدادات")
        st.markdown("---")

        model_choice = st.radio(
            "🧠 نوع النموذج",
            ["سريع (EncoderOnly)", "دقيق (EncoderDecoder)"],
            index=0,
        )
        fast_mode = model_choice == "سريع (EncoderOnly)"

        st.markdown("---")
        st.markdown("## 📝 نماذج جاهزة")

        for cat_name, cat_items in sample_categories.items():
            st.markdown(f"**{cat_name}**")
            for idx, txt in enumerate(cat_items):
                label = txt[:28] + "..." if len(txt) > 28 else txt
                if st.button(label, key=f"s_{cat_name}_{idx}", use_container_width=True):
                    selected_sample = txt

        st.markdown("---")
        st.markdown("## 🛠️ أدوات")
        strip_mode = st.checkbox("🔄 إزالة التشكيل", value=False)

        st.markdown("---")
        with st.expander("🔍 تشخيص المكتبات"):
            deps = check_dependencies()
            for lib, info in deps.items():
                if info["installed"]:
                    st.markdown(f"✅ **{lib}** `{info['version']}`")
                else:
                    st.markdown(f"❌ **{lib}**")
            st.caption(f"Python {sys.version_info.major}.{sys.version_info.minor}")

        st.markdown("---")
        st.markdown(
            "<p style='text-align:center;color:#555;font-size:0.75rem;'>"
            "صُنع بـ ❤️ للغة العربية</p>",
            unsafe_allow_html=True,
        )

    return fast_mode, selected_sample, strip_mode
