"""
تطبيق التشكيل الآلي للنصوص العربية
مبني على Streamlit مع واجهة عصرية
"""

import streamlit as st
import time
import json
from diacritizer import ArabicDiacritizer

# ═══════════════════════════════════════════
#            إعدادات الصفحة
# ═══════════════════════════════════════════
st.set_page_config(
    page_title="مُشكِّل النصوص العربية | CATT",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════
#            الأنماط CSS المخصصة
# ═══════════════════════════════════════════
st.markdown("""
<style>
    /* === الخطوط العربية === */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');

    /* === الإعدادات العامة === */
    * {
        font-family: 'Tajawal', sans-serif !important;
    }

    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    /* === العنوان الرئيسي === */
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(
            circle, rgba(233, 196, 106, 0.05) 0%, transparent 70%
        );
        animation: pulse 4s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 1; }
    }

    .main-header h1 {
        color: #e9c46a !important;
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        margin: 0 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }

    .main-header p {
        color: #a8dadc !important;
        font-size: 1.15rem !important;
        margin-top: 0.5rem !important;
        position: relative;
        z-index: 1;
    }

    /* === مربعات النص === */
    .stTextArea textarea {
        font-family: 'Amiri', serif !important;
        font-size: 1.35rem !important;
        line-height: 2.2 !important;
        direction: rtl !important;
        text-align: right !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 15px !important;
        padding: 1.2rem !important;
        transition: all 0.3s ease !important;
        background: #fafafa !important;
    }

    .stTextArea textarea:focus {
        border-color: #e9c46a !important;
        box-shadow: 0 0 0 3px rgba(233, 196, 106, 0.2) !important;
        background: #fff !important;
    }

    /* === الأزرار === */
    .stButton > button {
        width: 100%;
        padding: 0.9rem 2rem !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        border-radius: 15px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        letter-spacing: 1px;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #e9c46a 0%, #f4a261 100%) !important;
        color: #1a1a2e !important;
        box-shadow: 0 4px 15px rgba(233, 196, 106, 0.4) !important;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(233, 196, 106, 0.5) !important;
    }

    /* === بطاقات الإحصائيات === */
    .stat-card {
        background: linear-gradient(135deg, #16213e, #1a1a2e);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        border: 1px solid rgba(233, 196, 106, 0.2);
        transition: transform 0.3s ease;
    }

    .stat-card:hover {
        transform: translateY(-5px);
    }

    .stat-number {
        font-size: 2.2rem;
        font-weight: 900;
        color: #e9c46a;
        display: block;
        margin-bottom: 0.3rem;
    }

    .stat-label {
        font-size: 0.95rem;
        color: #a8dadc;
        font-weight: 500;
    }

    /* === النص المشكل === */
    .diacritized-output {
        background: linear-gradient(135deg, #fff9e6, #fff5d6);
        border: 2px solid #e9c46a;
        border-radius: 15px;
        padding: 2rem;
        direction: rtl;
        text-align: right;
        font-family: 'Amiri', serif !important;
        font-size: 1.6rem;
        line-height: 2.5;
        color: #1a1a2e;
        box-shadow: 0 4px 20px rgba(233, 196, 106, 0.15);
        min-height: 150px;
    }

    /* === الشريط الجانبي === */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }

    section[data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #e9c46a !important;
    }

    /* === نماذج جاهزة === */
    .sample-btn {
        background: rgba(233, 196, 106, 0.1);
        border: 1px solid rgba(233, 196, 106, 0.3);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin: 0.3rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        direction: rtl;
        text-align: right;
        color: #e0e0e0;
    }

    .sample-btn:hover {
        background: rgba(233, 196, 106, 0.2);
        border-color: #e9c46a;
    }

    /* === التوزيع الحركي === */
    .diacritic-bar {
        display: flex;
        align-items: center;
        margin: 0.4rem 0;
        direction: rtl;
    }

    .diacritic-name {
        min-width: 100px;
        color: #a8dadc;
        font-size: 0.9rem;
    }

    .diacritic-fill {
        height: 8px;
        border-radius: 4px;
        background: linear-gradient(90deg, #e9c46a, #f4a261);
        transition: width 0.5s ease;
    }

    .diacritic-count {
        min-width: 40px;
        text-align: left;
        color: #e9c46a;
        font-weight: 700;
        font-size: 0.9rem;
        margin-right: 0.5rem;
    }

    /* === رسالة الخطأ === */
    .error-box {
        background: rgba(231, 76, 60, 0.1);
        border: 1px solid rgba(231, 76, 60, 0.3);
        border-radius: 10px;
        padding: 1rem;
        color: #e74c3c;
        direction: rtl;
        text-align: right;
    }

    /* === الفوتر === */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        border-top: 1px solid #e0e0e0;
        margin-top: 3rem;
    }

    /* === إخفاء عناصر Streamlit الافتراضية === */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════
#            تحميل النموذج (مخزن مؤقتاً)
# ═══════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def load_model(fast_mode=True):
    """تحميل النموذج مرة واحدة وتخزينه"""
    return ArabicDiacritizer(fast_mode=fast_mode)


# ═══════════════════════════════════════════
#            النماذج الجاهزة
# ═══════════════════════════════════════════
SAMPLE_TEXTS = {
    "آية قرآنية": "ان الذين امنوا وعملوا الصالحات كانت لهم جنات الفردوس نزلا",
    "حديث شريف": "انما الاعمال بالنيات وانما لكل امرئ ما نوى",
    "شعر عربي": "قف على الاطلال واستنطق رسوما دارسات لعلها تبوح بما كتمت",
    "نثر أدبي": "اللغة العربية من اجمل اللغات واكثرها ثراء في المفردات والتراكيب",
    "نص تاريخي": "فتح المسلمون الاندلس في عهد الدولة الاموية وازدهرت الحضارة الاسلامية فيها",
    "حكمة": "من جد وجد ومن زرع حصد ومن سار على الدرب وصل",
    "نص علمي": "اسهم العلماء العرب في تطوير علوم الرياضيات والفلك والطب والكيمياء",
}


# ═══════════════════════════════════════════
#            الشريط الجانبي
# ═══════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ الإعدادات")
    st.markdown("---")

    # اختيار نوع النموذج
    model_mode = st.radio(
        "🧠 نوع النموذج",
        options=["سريع (EncoderOnly)", "دقيق (EncoderDecoder)"],
        index=0,
        help="النموذج السريع أسرع بكثير مع دقة جيدة جداً"
    )
    fast_mode = model_mode == "سريع (EncoderOnly)"

    st.markdown("---")
    st.markdown("## 📝 نماذج جاهزة")
    st.markdown("اختر نصاً جاهزاً للتجربة:")

    # أزرار النماذج
    selected_sample = None
    for name, text in SAMPLE_TEXTS.items():
        if st.button(f"📌 {name}", key=f"sample_{name}", use_container_width=True):
            selected_sample = text

    st.markdown("---")
    st.markdown("## 📊 معلومات النموذج")
    st.info(f"""
    **النموذج:** CATT Tashkeel
    **الوضع:** {"سريع ⚡" if fast_mode else "دقيق 🎯"}
    **المصدر:** [GitHub](https://github.com/GT-SALT/CATT)
    """)

    st.markdown("---")
    st.markdown("## 🛠️ أدوات إضافية")

    # تحميل النتائج
    if st.button("📥 تحميل آخر نتيجة", use_container_width=True):
        if 'last_result' in st.session_state and st.session_state.last_result:
            st.download_button(
                label="💾 حفظ كملف نصي",
                data=st.session_state.last_result,
                file_name="tashkeel_result.txt",
                mime="text/plain"
            )

    # إزالة التشكيل
    strip_mode = st.checkbox("🔄 وضع إزالة التشكيل", value=False)

    st.markdown("---")
    st.markdown(
        "<p style='text-align:center; color:#666; font-size:0.8rem;'>"
        "صُنع بـ ❤️ للغة العربية"
        "</p>",
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════
#            المحتوى الرئيسي
# ═══════════════════════════════════════════

# العنوان الرئيسي
st.markdown("""
<div class="main-header">
    <h1>✍️ مُشكِّل النصوص العربية</h1>
    <p>تشكيل آلي ذكي باستخدام نموذج CATT للذكاء الاصطناعي</p>
</div>
""", unsafe_allow_html=True)

# تحميل النموذج
with st.spinner("🔄 جاري تحميل نموذج الذكاء الاصطناعي... يرجى الانتظار"):
    diacritizer = load_model(fast_mode=fast_mode)

if not diacritizer.is_loaded:
    st.error("""
    ❌ **فشل تحميل النموذج!**

    تأكد من تثبيت المكتبة:
    ```bash
    pip install catt-tashkeel
    ```
    """)
    st.stop()

# حالة النموذج
st.success(f"✅ النموذج جاهز | الوضع: {diacritizer.model_type}")

# ═══════════════════════════════════════════
#            منطقة الإدخال والإخراج
# ═══════════════════════════════════════════

# تحديث الإدخال إذا تم اختيار نموذج
if selected_sample:
    st.session_state.input_text = selected_sample

# التبويبات
tab1, tab2, tab3 = st.tabs(["✍️ تشكيل فوري", "📄 معالجة ملف", "📊 تحليل"])

# ═══════════ التبويب الأول: تشكيل فوري ═══════════
with tab1:
    col_input, col_output = st.columns(2)

    with col_input:
        st.markdown("### 📝 النص الأصلي")
        input_text = st.text_area(
            label="أدخل النص العربي هنا",
            value=st.session_state.get('input_text', ''),
            height=250,
            placeholder="اكتب أو الصق النص العربي هنا...\n\nمثال: بسم الله الرحمن الرحيم",
            label_visibility="collapsed"
        )

        # عداد الكلمات
        word_count = len(input_text.split()) if input_text.strip() else 0
        char_count = len(input_text) if input_text else 0
        st.caption(f"📏 {word_count} كلمة | {char_count} حرف")

    with col_output:
        st.markdown("### ✨ النص المُشكَّل")
        output_placeholder = st.empty()
        output_placeholder.markdown(
            '<div class="diacritized-output" style="color:#999;">'
            'سيظهر النص المشكل هنا بعد الضغط على الزر...'
            '</div>',
            unsafe_allow_html=True
        )

    # أزرار التحكم
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])

    with col_btn1:
        tashkeel_clicked = st.button(
            "✍️ تشكيل النص" if not strip_mode else "🔄 إزالة التشكيل",
            type="primary",
            use_container_width=True
        )

    with col_btn2:
        clear_clicked = st.button(
            "🗑️ مسح",
            use_container_width=True
        )

    with col_btn3:
        copy_clicked = st.button(
            "📋 نسخ النتيجة",
            use_container_width=True
        )

    # معالجة الأزرار
    if clear_clicked:
        st.session_state.input_text = ''
        st.session_state.last_result = ''
        st.rerun()

    if tashkeel_clicked and input_text.strip():
        if strip_mode:
            # وضع إزالة التشكيل
            result_text = diacritizer.strip_diacritics(input_text)
            output_placeholder.markdown(
                f'<div class="diacritized-output">{result_text}</div>',
                unsafe_allow_html=True
            )
            st.session_state.last_result = result_text
        else:
            # وضع التشكيل
            with st.spinner("⏳ جاري التشكيل..."):
                result = diacritizer.process_text(input_text)

            if result['success']:
                # عرض النتيجة
                output_placeholder.markdown(
                    f'<div class="diacritized-output">'
                    f'{result["diacritized"]}'
                    f'</div>',
                    unsafe_allow_html=True
                )
                st.session_state.last_result = result['diacritized']

                # الإحصائيات السريعة
                st.markdown("---")
                st.markdown("### 📊 إحصائيات التشكيل")

                s1, s2, s3, s4 = st.columns(4)

                with s1:
                    st.markdown(f"""
                    <div class="stat-card">
                        <span class="stat-number">{result['stats']['words']}</span>
                        <span class="stat-label">كلمة</span>
                    </div>
                    """, unsafe_allow_html=True)

                with s2:
                    st.markdown(f"""
                    <div class="stat-card">
                        <span class="stat-number">{result['stats']['arabic_chars']}</span>
                        <span class="stat-label">حرف عربي</span>
                    </div>
                    """, unsafe_allow_html=True)

                with s3:
                    st.markdown(f"""
                    <div class="stat-card">
                        <span class="stat-number">{result['stats']['total_diacritics']}</span>
                        <span class="stat-label">حركة مُضافة</span>
                    </div>
                    """, unsafe_allow_html=True)

                with s4:
                    st.markdown(f"""
                    <div class="stat-card">
                        <span class="stat-number">{result['processing_time']}s</span>
                        <span class="stat-label">وقت المعالجة</span>
                    </div>
                    """, unsafe_allow_html=True)

                # توزيع الحركات
                if result['stats']['diacritic_breakdown']:
                    st.markdown("#### 🔤 توزيع الحركات")
                    breakdown = result['stats']['diacritic_breakdown']
                    max_count = max(breakdown.values()) if breakdown else 1

                    for name, count in sorted(
                        breakdown.items(), key=lambda x: x[1], reverse=True
                    ):
                        percentage = (count / max_count) * 100
                        col_a, col_b, col_c = st.columns([1, 3, 0.5])
                        with col_a:
                            st.markdown(
                                f"<span style='color:#a8dadc'>{name}</span>",
                                unsafe_allow_html=True
                            )
                        with col_b:
                            st.progress(percentage / 100)
                        with col_c:
                            st.markdown(
                                f"**{count}**"
                            )

            else:
                st.markdown(
                    f'<div class="error-box">❌ {result["error"]}</div>',
                    unsafe_allow_html=True
                )

    elif tashkeel_clicked:
        st.warning("⚠️ الرجاء إدخال نص عربي أولاً")

    # نسخ النتيجة
    if copy_clicked and 'last_result' in st.session_state:
        st.code(st.session_state.last_result, language=None)
        st.info("📋 انسخ النص من الصندوق أعلاه")


# ═══════════ التبويب الثاني: معالجة ملف ═══════════
with tab2:
    st.markdown("### 📄 تشكيل ملف نصي كامل")
    st.markdown("ارفع ملفاً نصياً (.txt) وسيتم تشكيله بالكامل")

    uploaded_file = st.file_uploader(
        "اختر ملفاً نصياً",
        type=['txt'],
        help="يدعم ملفات .txt بترميز UTF-8"
    )

    if uploaded_file is not None:
        # قراءة الملف
        file_content = uploaded_file.read().decode('utf-8')
        st.text_area("محتوى الملف:", value=file_content, height=150, disabled=True)

        if st.button("✍️ تشكيل الملف بالكامل", type="primary"):
            with st.spinner("⏳ جاري تشكيل الملف..."):
                # تقسيم النص لأجزاء لتسريع المعالجة
                paragraphs = file_content.split('\n')
                results = []
                progress_bar = st.progress(0)

                for i, para in enumerate(paragraphs):
                    if para.strip():
                        result = diacritizer.quick_tashkeel(para)
                        results.append(result)
                    else:
                        results.append('')
                    progress_bar.progress((i + 1) / len(paragraphs))

                full_result = '\n'.join(results)
                progress_bar.empty()

            st.markdown("### ✨ النتيجة:")
            st.text_area("النص المشكل:", value=full_result, height=200)

            # زر التحميل
            st.download_button(
                label="💾 تحميل النتيجة",
                data=full_result.encode('utf-8'),
                file_name=f"tashkeel_{uploaded_file.name}",
                mime="text/plain"
            )


# ═══════════ التبويب الثالث: تحليل ═══════════
with tab3:
    st.markdown("### 📊 تحليل ومقارنة النصوص")
    st.markdown("أدخل نصاً مشكلاً يدوياً لمقارنته مع تشكيل النموذج")

    col_ref, col_auto = st.columns(2)

    with col_ref:
        ref_text = st.text_area(
            "النص المشكل يدوياً (المرجع):",
            height=150,
            placeholder="أدخل النص المشكل يدوياً هنا..."
        )

    with col_auto:
        auto_text = st.text_area(
            "النص غير المشكل:",
            height=150,
            placeholder="أدخل النص بدون تشكيل هنا..."
        )

    if st.button("📊 تحليل ومقارنة", type="primary"):
        if auto_text.strip():
            result = diacritizer.process_text(auto_text)

            if result['success']:
                st.markdown("#### نتيجة التشكيل الآلي:")
                st.markdown(
                    f'<div class="diacritized-output">{result["diacritized"]}</div>',
                    unsafe_allow_html=True
                )

                if ref_text.strip():
                    # مقارنة بسيطة
                    auto_clean = diacritizer.strip_diacritics(result['diacritized'])
                    ref_clean = diacritizer.strip_diacritics(ref_text)

                    if auto_clean == ref_clean:
                        st.success("✅ النصان الأساسيان متطابقان - يمكن المقارنة")
                    else:
                        st.warning("⚠️ النصان الأساسيان مختلفان - قد لا تكون المقارنة دقيقة")


# ═══════════════════════════════════════════
#            الفوتر
# ═══════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>✍️ <strong>مُشكِّل النصوص العربية</strong> | مبني على نموذج CATT للذكاء الاصطناعي</p>
    <p>صُنع بـ ❤️ للغة العربية | Streamlit + Python</p>
</div>
""", unsafe_allow_html=True)
