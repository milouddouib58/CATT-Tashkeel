"""تبويب معالجة الملفات"""

import streamlit as st


def render_tab_file(diacritizer, is_demo):
    """عرض تبويب الملفات"""
    st.markdown("### 📄 تشكيل ملف نصي")

    if is_demo:
        st.info(
            "⚡ معالجة الملفات تحتاج النموذج الحقيقي.\n\n"
            "شغّل محلياً:\n"
            "```\npip install catt-tashkeel streamlit\n"
            "streamlit run app_streamlit.py\n```"
        )
        return

    uploaded = st.file_uploader("اختر ملف .txt", type=["txt"], key="fup")

    if uploaded is None:
        return

    try:
        content = uploaded.read().decode("utf-8")
    except UnicodeDecodeError:
        st.error("❌ الملف ليس UTF-8")
        return

    st.text_area("المحتوى:", value=content, height=150, disabled=True, key="fprev")

    lines = content.split("\n")
    st.caption(f"📏 {len(lines)} سطر | {len(content)} حرف")

    if not st.button("✍️ تشكيل الملف", type="primary", key="btn_frun"):
        return

    with st.spinner("⏳ جاري التشكيل..."):
        out = []
        bar = st.progress(0)
        for i, line in enumerate(lines):
            if line.strip():
                out.append(diacritizer.quick_tashkeel(line))
            else:
                out.append("")
            bar.progress((i + 1) / len(lines))
        bar.empty()
        full = "\n".join(out)

    st.success("✅ تم!")
    st.text_area("النتيجة:", value=full, height=200, key="fres")
    st.download_button(
        "💾 تحميل",
        data=full.encode("utf-8"),
        file_name=f"tashkeel_{uploaded.name}",
        mime="text/plain",
        key="btn_fdl",
    )
