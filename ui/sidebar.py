"""
الشريط الجانبي للتطبيق
يحتوي على: إعدادات النموذج، النماذج الجاهزة، الأدوات

القيمة المرجعة من render_sidebar:
    tuple(fast_mode, selected_sample, strip_mode)
"""

import streamlit as st
from helpers import check_dependencies


def render_sidebar(sample_categories: dict) -> tuple:
    """
    عرض الشريط الجانبي وإرجاع إعدادات المستخدم

    المعاملات:
        sample_categories: تصنيف النماذج الجاهزة

    القيمة المرجعة:
        (fast_mode, selected_sample, strip_mode)
    """
    selected_sample = None

    with st.sidebar:
        # ── الإعدادات ──
        st.markdown("## ⚙️ الإعدادات")
        st.markdown("---")

        model_choice = st.radio(
            "🧠 نوع النموذج",
            options=[
                "سريع (EncoderOnly)",
                "دقيق (EncoderDecoder)",
            ],
            index=0,
            help=(
                "**السريع:** أقل استهلاكاً للذاكرة وأسرع.\n\n"
                "**الدقيق:** أعلى جودة لكن أبطأ وأكثر استهلاكاً."
            ),
        )
        fast_mode = model_choice == "سريع (EncoderOnly)"

        # ── النماذج الجاهزة ──
        st.markdown("---")
        st.markdown("## 📝 نماذج جاهزة")

        for cat_name, cat_items in sample_categories.items():
            st.markdown(f"**{cat_name}**")
            for idx, sample_txt in enumerate(cat_items):
                # اختصار النص الطويل
                display = (
                    sample_txt[:28] + "..."
                    if len(sample_txt) > 28
                    else sample_txt
                )
                btn_key = f"sb_{cat_name}_{idx}"

                if st.button(
                    display,
                    key=btn_key,
                    use_container_width=True,
                ):
                    selected_sample = sample_txt

        # ── أدوات إضافية ──
        st.markdown("---")
        st.markdown("## 🛠️ أدوات")
        strip_mode = st.checkbox(
            "🔄 وضع إزالة التشكيل",
            value=False,
            help="تحويل الوضع لإزالة التشكيل من النص بدلاً من إضافته",
        )

        # ── التشخيص ──
        st.markdown("---")
        with st.expander("🔍 تشخيص المكتبات"):
            _render_diagnostics()

        # ── ذيل الشريط الجانبي ──
        st.markdown("---")
        st.markdown(
            "<p style='text-align:center; color:#555; "
            "font-size:0.75rem;'>صُنع بـ ❤️ للغة العربية</p>",
            unsafe_allow_html=True,
        )

    return fast_mode, selected_sample, strip_mode


def _render_diagnostics():
    """عرض تقرير تشخيص المكتبات"""
    import sys

    deps = check_dependencies()

    for lib_name, lib_info in deps.items():
        if lib_info["installed"]:
            st.markdown(
                f"✅ **{lib_name}** `{lib_info['version']}`"
            )
        else:
            st.markdown(
                f"❌ **{lib_name}** — غير مثبت"
            )

    st.caption(
        f"Python {sys.version_info.major}."
        f"{sys.version_info.minor}."
        f"{sys.version_info.micro}"
    )
