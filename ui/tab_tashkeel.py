"""
تبويب التشكيل الفوري
الوظيفة الرئيسية: إدخال نص → تشكيل → عرض النتيجة مع إحصائيات
"""

import streamlit as st
from helpers import do_tashkeel


def render_tab_tashkeel(diacritizer, is_demo: bool, strip_mode: bool):
    """
    عرض تبويب التشكيل الفوري

    المعاملات:
        diacritizer: كائن محرك التشكيل
        is_demo: هل نحن في الوضع التجريبي
        strip_mode: هل وضع إزالة التشكيل مفعّل
    """

    # ── منطقة الإدخال والإخراج ──
    col_in, col_out = st.columns(2, gap="large")

    with col_in:
        st.markdown("### 📝 النص الأصلي")
        input_text = st.text_area(
            label="أدخل النص",
            value=st.session_state.get("input_text", ""),
            height=260,
            placeholder=(
                "اكتب أو الصق النص العربي هنا...\n\n"
                "مثال: بسم الله الرحمن الرحيم"
            ),
            label_visibility="collapsed",
            key="main_input",
        )

        # عدّاد الكلمات والحروف
        wc = len(input_text.split()) if input_text.strip() else 0
        cc = len(input_text)
        st.caption(f"📏 {wc} كلمة &nbsp;|&nbsp; {cc} حرف")

    with col_out:
        st.markdown("### ✨ النص المُشكَّل")
        out_holder = st.empty()
        out_holder.markdown(
            '<div class="result-box result-box-empty">'
            "سيظهر النص المُشكَّل هنا ⬇️"
            "</div>",
            unsafe_allow_html=True,
        )

    # ── أزرار التحكم ──
    bc1, bc2, bc3 = st.columns([3, 1, 1])

    with bc1:
        btn_label = (
            "🔄 إزالة التشكيل" if strip_mode
            else "✍️ تشكيل النص"
        )
        run_btn = st.button(
            btn_label,
            type="primary",
            use_container_width=True,
            key="btn_run",
        )

    with bc2:
        clr_btn = st.button(
            "🗑️ مسح",
            use_container_width=True,
            key="btn_clear",
        )

    with bc3:
        cpy_btn = st.button(
            "📋 نسخ",
            use_container_width=True,
            key="btn_copy",
        )

    # ── معالجة زر المسح ──
    if clr_btn:
        st.session_state["input_text"] = ""
        st.session_state["last_result"] = ""
        st.rerun()

    # ── معالجة زر التشكيل ──
    if run_btn:
        if not input_text.strip():
            st.warning("⚠️ الرجاء إدخال نص عربي أولاً")
        elif strip_mode:
            _handle_strip(diacritizer, input_text, out_holder)
        else:
            _handle_tashkeel(
                diacritizer, input_text, is_demo, out_holder
            )

    # ── معالجة زر النسخ ──
    if cpy_btn:
        _handle_copy()


def _handle_strip(diacritizer, text, out_holder):
    """معالجة وضع إزالة التشكيل"""
    stripped = diacritizer.strip_diacritics(text)
    out_holder.markdown(
        f'<div class="result-box">{stripped}</div>',
        unsafe_allow_html=True,
    )
    st.session_state["last_result"] = stripped
    st.success("✅ تمت إزالة التشكيل بنجاح")


def _handle_tashkeel(diacritizer, text, is_demo, out_holder):
    """معالجة وضع التشكيل"""
    with st.spinner("⏳ جاري التشكيل..."):
        result = do_tashkeel(text, diacritizer)

    if not result["success"]:
        st.warning(result["error"])
        return

    # عرض النتيجة
    out_holder.markdown(
        f'<div class="result-box">{result["diacritized"]}</div>',
        unsafe_allow_html=True,
    )
    st.session_state["last_result"] = result["diacritized"]

    # شارة الوضع التجريبي
    if result.get("demo"):
        st.markdown(
            '<div class="demo-notice">'
            "⚡ نتيجة من النماذج المُشكّلة مسبقاً"
            "</div>",
            unsafe_allow_html=True,
        )

    # الإحصائيات
    _render_stats(result)


def _render_stats(result: dict):
    """عرض إحصائيات التشكيل"""
    stats = result.get("stats", {})
    if not stats:
        return

    st.markdown("---")
    st.markdown("### 📊 إحصائيات التشكيل")

    # البطاقات الأربع
    m1, m2, m3, m4 = st.columns(4)

    cards = [
        (m1, stats.get("words", 0), "كلمة"),
        (m2, stats.get("arabic_chars", 0), "حرف عربي"),
        (m3, stats.get("total_diacritics", 0), "حركة مُضافة"),
        (m4, f'{result.get("processing_time", 0)}s', "وقت المعالجة"),
    ]

    for col, value, label in cards:
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<span class="metric-val">{value}</span>'
                f'<span class="metric-lbl">{label}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )

    # توزيع الحركات
    breakdown = stats.get("breakdown", {})
    if not breakdown:
        return

    st.markdown("#### 🔤 توزيع الحركات")
    max_val = max(breakdown.values())

    for name, count in sorted(
        breakdown.items(), key=lambda x: x[1], reverse=True
    ):
        pct = count / max_val if max_val > 0 else 0
        ca, cb, cc = st.columns([1, 3, 0.5])

        with ca:
            st.markdown(
                f"<span style='color:#a8dadc;'>{name}</span>",
                unsafe_allow_html=True,
            )
        with cb:
            st.progress(pct)
        with cc:
            st.markdown(f"**{count}**")


def _handle_copy():
    """معالجة زر النسخ"""
    last = st.session_state.get("last_result", "")
    if last:
        st.code(last, language=None)
        st.info("📋 حدّد النص من الصندوق أعلاه ثم Ctrl+C")
    else:
        st.warning("⚠️ لا توجد نتيجة للنسخ بعد")
