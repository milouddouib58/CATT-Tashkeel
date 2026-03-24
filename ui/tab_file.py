"""
تبويب معالجة الملفات النصية
يتيح رفع ملف .txt وتشكيله بالكامل مع شريط تقدم
"""

import streamlit as st


def render_tab_file(diacritizer, is_demo: bool):
    """
    عرض تبويب معالجة الملفات

    المعاملات:
        diacritizer: كائن محرك التشكيل
        is_demo: هل نحن في الوضع التجريبي
    """
    st.markdown("### 📄 تشكيل ملف نصي كامل")
    st.markdown("ارفع ملف `.txt` بترميز UTF-8")

    # الوضع التجريبي لا يدعم الملفات
    if is_demo:
        st.info(
            "⚡ **معالجة الملفات** تحتاج إلى النموذج الحقيقي.\n\n"
            "شغّل التطبيق **محلياً** لاستخدام هذه الميزة:\n"
            "```\n"
            "pip install catt-tashkeel streamlit\n"
            "streamlit run app_streamlit.py\n"
            "```"
        )
        return

    # رفع الملف
    uploaded = st.file_uploader(
        "اختر ملفاً نصياً",
        type=["txt"],
        key="file_uploader",
    )

    if uploaded is None:
        return

    # قراءة المحتوى
    try:
        content = uploaded.read().decode("utf-8")
    except UnicodeDecodeError:
        st.error("❌ الملف ليس بترميز UTF-8. يرجى تحويله أولاً.")
        return

    # عرض المحتوى الأصلي
    st.text_area(
        "📄 المحتوى الأصلي:",
        value=content,
        height=150,
        disabled=True,
        key="file_preview",
    )

    # معلومات الملف
    lines = content.split("\n")
    total_words = sum(len(line.split()) for line in lines if line.strip())
    st.caption(
        f"📏 {len(lines)} سطر &nbsp;|&nbsp; "
        f"{total_words} كلمة &nbsp;|&nbsp; "
        f"{len(content)} حرف"
    )

    # زر التشكيل
    if not st.button(
        "✍️ تشكيل الملف بالكامل",
        type="primary",
        key="btn_file_tashkeel",
    ):
        return

    # المعالجة
    with st.spinner("⏳ جاري تشكيل الملف..."):
        out_lines = []
        bar = st.progress(0, text="جاري المعالجة...")

        for i, line in enumerate(lines):
            if line.strip():
                out_lines.append(
                    diacritizer.quick_tashkeel(line)
                )
            else:
                out_lines.append("")

            progress = (i + 1) / len(lines)
            bar.progress(
                progress,
                text=f"تم معالجة {i + 1} من {len(lines)} سطر",
            )

        bar.empty()
        full_result = "\n".join(out_lines)

    # عرض النتيجة
    st.success("✅ تم تشكيل الملف بنجاح!")
    st.markdown("### ✨ النتيجة:")
    st.text_area(
        "النص المشكل:",
        value=full_result,
        height=200,
        key="file_result",
    )

    # زر التحميل
    st.download_button(
        label="💾 تحميل النتيجة",
        data=full_result.encode("utf-8"),
        file_name=f"tashkeel_{uploaded.name}",
        mime="text/plain",
        key="btn_download",
    )
