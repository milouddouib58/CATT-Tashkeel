"""تبويب التشكيل الفوري"""

import streamlit as st
from helpers import do_tashkeel


def render_tab_tashkeel(diacritizer, is_demo, strip_mode):
    """عرض تبويب التشكيل"""

    col_in, col_out = st.columns(2, gap="large")

    with col_in:
        st.markdown("### 📝 النص الأصلي")
        input_text = st.text_area(
            label="أدخل النص",
            value=st.session_state.get("input_text", ""),
            height=260,
            placeholder="اكتب أو الصق النص العربي هنا...",
            label_visibility="collapsed",
            key="main_input",
        )
        wc = len(input_text.split()) if input_text.strip() else 0
        st.caption(f"📏 {wc} كلمة | {len(input_text)} حرف")

    with col_out:
        st.markdown("### ✨ النص المُشكَّل")
        out_holder = st.empty()
        out_holder.markdown(
            '<div class="result-box result-box-empty">'
            "سيظهر النص المُشكَّل هنا ⬇️</div>",
            unsafe_allow_html=True,
        )

    # الأزرار
    c1, c2, c3 = st.columns([3, 1, 1])

    with c1:
        label = "🔄 إزالة التشكيل" if strip_mode else "✍️ تشكيل النص"
        run = st.button(label, type="primary", use_container_width=True, key="btn_run")

    with c2:
        clr = st.button("🗑️ مسح", use_container_width=True, key="btn_clr")

    with c3:
        cpy = st.button("📋 نسخ", use_container_width=True, key="btn_cpy")

    # مسح
    if clr:
        st.session_state["input_text"] = ""
        st.session_state["last_result"] = ""
        st.rerun()

    # تشكيل
    if run:
        if not input_text.strip():
            st.warning("⚠️ أدخل نصاً أولاً")
        elif strip_mode:
            stripped = diacritizer.strip_diacritics(input_text)
            out_holder.markdown(
                f'<div class="result-box">{stripped}</div>',
                unsafe_allow_html=True,
            )
            st.session_state["last_result"] = stripped
            st.success("✅ تمت إزالة التشكيل")
        else:
            with st.spinner("⏳ جاري التشكيل..."):
                result = do_tashkeel(input_text, diacritizer)

            if result["success"]:
                out_holder.markdown(
                    f'<div class="result-box">{result["diacritized"]}</div>',
                    unsafe_allow_html=True,
                )
                st.session_state["last_result"] = result["diacritized"]

                if result.get("demo"):
                    st.markdown(
                        '<div class="demo-notice">'
                        "⚡ نتيجة من النماذج الجاهزة</div>",
                        unsafe_allow_html=True,
                    )

                _show_stats(result)
            else:
                st.warning(result["error"])

    # نسخ
    if cpy:
        last = st.session_state.get("last_result", "")
        if last:
            st.code(last, language=None)
            st.info("📋 حدّد النص وانسخه Ctrl+C")
        else:
            st.warning("⚠️ لا توجد نتيجة للنسخ")


def _show_stats(result):
    """عرض الإحصائيات"""
    stats = result.get("stats", {})
    if not stats:
        return

    st.markdown("---")
    st.markdown("### 📊 إحصائيات التشكيل")

    m1, m2, m3, m4 = st.columns(4)

    data = [
        (m1, stats.get("words", 0), "كلمة"),
        (m2, stats.get("arabic_chars", 0), "حرف عربي"),
        (m3, stats.get("total_diacritics", 0), "حركة"),
        (m4, f'{result.get("processing_time", 0)}s', "الوقت"),
    ]

    for col, val, lbl in data:
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<span class="metric-val">{val}</span>'
                f'<span class="metric-lbl">{lbl}</span></div>',
                unsafe_allow_html=True,
            )

    bd = stats.get("breakdown", {})
    if bd:
        st.markdown("#### 🔤 توزيع الحركات")
        mx = max(bd.values()) if bd else 1
        for name, count in sorted(bd.items(), key=lambda x: x[1], reverse=True):
            ca, cb, cc = st.columns([1, 3, 0.5])
            with ca:
                st.markdown(f"<span style='color:#a8dadc;'>{name}</span>", unsafe_allow_html=True)
            with cb:
                st.progress(count / mx if mx else 0)
            with cc:
                st.markdown(f"**{count}**")
