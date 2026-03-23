"""
مُشكِّل النصوص العربية - CATT Tashkeel
ملف واحد متكامل للنشر على Streamlit Cloud
"""

import streamlit as st
import logging
import time
import re

# ═══════════════════════════════════════════
#          إعداد السجلات
# ═══════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════
#          كلاس محرك التشكيل
# ═══════════════════════════════════════════
class ArabicDiacritizer:
    """محرك التشكيل الآلي للنصوص العربية"""

    DIACRITICS = {
        "\u064B": "تنوين فتح",
        "\u064C": "تنوين ضم",
        "\u064D": "تنوين كسر",
        "\u064E": "فتحة",
        "\u064F": "ضمة",
        "\u0650": "كسرة",
        "\u0651": "شدة",
        "\u0652": "سكون",
    }

    DIACRITIC_PATTERN = re.compile(
        "[\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0670]"
    )

    def __init__(self, fast_mode=True):
        self.fast_mode = fast_mode
        self.model = None
        self.is_loaded = False
        self.model_type = ""
        self._load_model()

    def _load_model(self):
        try:
            logger.info("جاري تحميل نموذج CATT...")
            start = time.time()

            if self.fast_mode:
                from catt_tashkeel import CATTEncoderOnly
                self.model = CATTEncoderOnly()
                self.model_type = "EncoderOnly (سريع)"
            else:
                from catt_tashkeel import CATTEncoderDecoder
                self.model = CATTEncoderDecoder()
                self.model_type = "EncoderDecoder (دقيق)"

            elapsed = time.time() - start
            logger.info(
                f"تم تحميل النموذج {self.model_type} "
                f"في {elapsed:.2f} ثانية"
            )
            self.is_loaded = True

        except ImportError as e:
            logger.error(f"خطأ في استيراد المكتبة: {e}")
            self.is_loaded = False

        except Exception as e:
            logger.error(f"خطأ في تحميل النموذج: {e}")
            self.is_loaded = False

    def process_text(self, text):
        """تشكيل النص مع إرجاع النتائج والإحصائيات"""
        result = {
            "original": text,
            "diacritized": "",
            "success": False,
            "error": None,
            "stats": {},
            "processing_time": 0,
        }

        if not text or not text.strip():
            result["error"] = "الرجاء إدخال نص عربي"
            return result

        if not self.is_loaded:
            result["error"] = "النموذج غير محمل"
            return result

        try:
            clean_text = self.strip_diacritics(text)
            start = time.time()
            diacritized = self.model.do_tashkeel(clean_text, verbose=False)
            elapsed = time.time() - start

            stats = self._calculate_stats(clean_text, diacritized)

            result["diacritized"] = diacritized
            result["success"] = True
            result["processing_time"] = round(elapsed, 3)
            result["stats"] = stats

        except Exception as e:
            logger.error(f"خطأ في التشكيل: {e}")
            result["error"] = str(e)

        return result

    def quick_tashkeel(self, text):
        """تشكيل سريع يرجع النص فقط"""
        if not text or not text.strip():
            return ""
        if not self.is_loaded:
            return "النموذج غير محمل"
        try:
            clean = self.strip_diacritics(text)
            return self.model.do_tashkeel(clean, verbose=False)
        except Exception as e:
            return f"خطأ: {e}"

    def strip_diacritics(self, text):
        """إزالة جميع الحركات من النص"""
        return self.DIACRITIC_PATTERN.sub("", text)

    def _calculate_stats(self, original, diacritized):
        """حساب إحصائيات التشكيل"""
        arabic_chars = len(
            re.findall(r"[\u0600-\u06FF]", original)
        )
        diacritics_added = len(
            re.findall(r"[\u064B-\u0652]", diacritized)
        )
        words = len(original.split())

        diacritic_counts = {}
        for d, name in self.DIACRITICS.items():
            count = diacritized.count(d)
            if count > 0:
                diacritic_counts[name] = count

        coverage = 0
        if arabic_chars > 0:
            coverage = round((diacritics_added / arabic_chars * 100), 1)

        return {
            "arabic_chars": arabic_chars,
            "total_diacritics": diacritics_added,
            "words": words,
            "coverage": coverage,
            "diacritic_breakdown": diacritic_counts,
        }


# ═══════════════════════════════════════════
#          إعدادات صفحة Streamlit
# ═══════════════════════════════════════════
st.set_page_config(
    page_title="مُشكِّل النصوص العربية | CATT",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ═══════════════════════════════════════════
#          أنماط CSS
# ═══════════════════════════════════════════
st.markdown(
    """
<style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;900&display=swap'
    );
    @import url(
        'https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap'
    );

    * {
        font-family: 'Tajawal', sans-serif !important;
    }

    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    .main-header {
        background: linear-gradient(
            135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%
        );
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
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(
            circle,
            rgba(233, 196, 106, 0.05) 0%,
            transparent 70%
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

    .stButton > button {
        width: 100%;
        padding: 0.9rem 2rem !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        border-radius: 15px !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }

    .stat-card {
        background: linear-gradient(135deg, #16213e, #1a1a2e);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        border: 1px solid rgba(233, 196, 106, 0.2);
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

    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg, #1a1a2e 0%, #16213e 100%
        );
    }

    section[data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #e9c46a !important;
    }

    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        border-top: 1px solid #e0e0e0;
        margin-top: 3rem;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════
#          تحميل النموذج (مخزن مؤقتاً)
# ═══════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def load_model(fast_mode=True):
    """تحميل النموذج مرة واحدة فقط"""
    return ArabicDiacritizer(fast_mode=fast_mode)


# ═══════════════════════════════════════════
#          النماذج الجاهزة
# ═══════════════════════════════════════════
SAMPLE_TEXTS = {
    "آية قرآنية": (
        "ان الذين امنوا وعملوا الصالحات "
        "كانت لهم جنات الفردوس نزلا"
    ),
    "حديث شريف": (
        "انما الاعمال بالنيات "
        "وانما لكل امرئ ما نوى"
    ),
    "شعر عربي": (
        "قف على الاطلال واستنطق رسوما "
        "دارسات لعلها تبوح بما كتمت"
    ),
    "نثر أدبي": (
        "اللغة العربية من اجمل اللغات "
        "واكثرها ثراء في المفردات والتراكيب"
    ),
    "نص تاريخي": (
        "فتح المسلمون الاندلس في عهد الدولة الاموية "
        "وازدهرت الحضارة الاسلامية فيها"
    ),
    "حكمة": (
        "من جد وجد ومن زرع حصد "
        "ومن سار على الدرب وصل"
    ),
}


# ═══════════════════════════════════════════
#          الشريط الجانبي
# ═══════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ الإعدادات")
    st.markdown("---")

    model_mode = st.radio(
        "🧠 نوع النموذج",
        options=["سريع (EncoderOnly)", "دقيق (EncoderDecoder)"],
        index=0,
        help="النموذج السريع أسرع بكثير مع دقة جيدة جداً",
    )
    fast_mode = model_mode == "سريع (EncoderOnly)"

    st.markdown("---")
    st.markdown("## 📝 نماذج جاهزة")
    st.markdown("اختر نصاً جاهزاً للتجربة:")

    selected_sample = None
    for name, text in SAMPLE_TEXTS.items():
        if st.button(
            f"📌 {name}",
            key=f"sample_{name}",
            use_container_width=True,
        ):
            selected_sample = text

    st.markdown("---")
    st.markdown("## 📊 معلومات النموذج")
    st.info(
        f"**النموذج:** CATT Tashkeel\n\n"
        f'**الوضع:** {"سريع ⚡" if fast_mode else "دقيق 🎯"}'
    )

    st.markdown("---")
    st.markdown("## 🛠️ أدوات إضافية")
    strip_mode = st.checkbox("🔄 وضع إزالة التشكيل", value=False)

    st.markdown("---")
    st.markdown(
        "<p style='text-align:center; color:#666; "
        "font-size:0.8rem;'>"
        "صُنع بـ ❤️ للغة العربية</p>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════
#          المحتوى الرئيسي
# ═══════════════════════════════════════════

# العنوان
st.markdown(
    """
<div class="main-header">
    <h1>✍️ مُشكِّل النصوص العربية</h1>
    <p>تشكيل آلي ذكي باستخدام نموذج CATT للذكاء الاصطناعي</p>
</div>
""",
    unsafe_allow_html=True,
)

# تحميل النموذج
with st.spinner(
    "🔄 جاري تحميل نموذج الذكاء الاصطناعي... يرجى الانتظار"
):
    diacritizer = load_model(fast_mode=fast_mode)

if not diacritizer.is_loaded:
    st.error(
        "❌ **فشل تحميل النموذج!**\n\n"
        "تأكد من تثبيت المكتبة:\n"
        "```\npip install catt-tashkeel\n```"
    )
    st.stop()

st.success(f"✅ النموذج جاهز | الوضع: {diacritizer.model_type}")

# تحديث الإدخال من النماذج الجاهزة
if selected_sample:
    st.session_state["input_text"] = selected_sample

# ═══════════════════════════════════════════
#          التبويبات
# ═══════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(
    ["✍️ تشكيل فوري", "📄 معالجة ملف", "📊 تحليل"]
)

# ═══════════ التبويب الأول ═══════════
with tab1:
    col_input, col_output = st.columns(2)

    with col_input:
        st.markdown("### 📝 النص الأصلي")
        input_text = st.text_area(
            label="أدخل النص العربي هنا",
            value=st.session_state.get("input_text", ""),
            height=250,
            placeholder=(
                "اكتب أو الصق النص العربي هنا...\n\n"
                "مثال: بسم الله الرحمن الرحيم"
            ),
            label_visibility="collapsed",
        )

        word_count = len(input_text.split()) if input_text.strip() else 0
        char_count = len(input_text) if input_text else 0
        st.caption(f"📏 {word_count} كلمة | {char_count} حرف")

    with col_output:
        st.markdown("### ✨ النص المُشكَّل")
        output_placeholder = st.empty()
        output_placeholder.markdown(
            '<div class="diacritized-output" '
            'style="color:#999;">'
            "سيظهر النص المشكل هنا بعد الضغط على الزر..."
            "</div>",
            unsafe_allow_html=True,
        )

    # أزرار التحكم
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])

    with col_btn1:
        if strip_mode:
            btn_label = "🔄 إزالة التشكيل"
        else:
            btn_label = "✍️ تشكيل النص"
        tashkeel_clicked = st.button(
            btn_label,
            type="primary",
            use_container_width=True,
        )

    with col_btn2:
        clear_clicked = st.button("🗑️ مسح", use_container_width=True)

    with col_btn3:
        copy_clicked = st.button(
            "📋 نسخ النتيجة", use_container_width=True
        )

    # مسح
    if clear_clicked:
        st.session_state["input_text"] = ""
        st.session_state["last_result"] = ""
        st.rerun()

    # تشكيل
    if tashkeel_clicked and input_text.strip():
        if strip_mode:
            result_text = diacritizer.strip_diacritics(input_text)
            output_placeholder.markdown(
                f'<div class="diacritized-output">'
                f"{result_text}</div>",
                unsafe_allow_html=True,
            )
            st.session_state["last_result"] = result_text
        else:
            with st.spinner("⏳ جاري التشكيل..."):
                result = diacritizer.process_text(input_text)

            if result["success"]:
                output_placeholder.markdown(
                    f'<div class="diacritized-output">'
                    f'{result["diacritized"]}</div>',
                    unsafe_allow_html=True,
                )
                st.session_state["last_result"] = result["diacritized"]

                # الإحصائيات
                st.markdown("---")
                st.markdown("### 📊 إحصائيات التشكيل")

                s1, s2, s3, s4 = st.columns(4)

                with s1:
                    st.markdown(
                        f'<div class="stat-card">'
                        f'<span class="stat-number">'
                        f'{result["stats"]["words"]}</span>'
                        f'<span class="stat-label">كلمة</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                with s2:
                    st.markdown(
                        f'<div class="stat-card">'
                        f'<span class="stat-number">'
                        f'{result["stats"]["arabic_chars"]}</span>'
                        f'<span class="stat-label">حرف عربي</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                with s3:
                    st.markdown(
                        f'<div class="stat-card">'
                        f'<span class="stat-number">'
                        f'{result["stats"]["total_diacritics"]}</span>'
                        f'<span class="stat-label">'
                        f"حركة مُضافة</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                with s4:
                    st.markdown(
                        f'<div class="stat-card">'
                        f'<span class="stat-number">'
                        f'{result["processing_time"]}s</span>'
                        f'<span class="stat-label">'
                        f"وقت المعالجة</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                # توزيع الحركات
                breakdown = result["stats"].get("diacritic_breakdown", {})
                if breakdown:
                    st.markdown("#### 🔤 توزيع الحركات")
                    for name, count in sorted(
                        breakdown.items(),
                        key=lambda x: x[1],
                        reverse=True,
                    ):
                        max_val = max(breakdown.values())
                        pct = count / max_val if max_val > 0 else 0
                        col_a, col_b, col_c = st.columns([1, 3, 0.5])
                        with col_a:
                            st.markdown(
                                f"<span style='color:#a8dadc'>"
                                f"{name}</span>",
                                unsafe_allow_html=True,
                            )
                        with col_b:
                            st.progress(pct)
                        with col_c:
                            st.markdown(f"**{count}**")

            else:
                st.error(f'❌ {result["error"]}')

    elif tashkeel_clicked:
        st.warning("⚠️ الرجاء إدخال نص عربي أولاً")

    # نسخ
    if copy_clicked and "last_result" in st.session_state:
        if st.session_state["last_result"]:
            st.code(st.session_state["last_result"], language=None)
            st.info("📋 انسخ النص من الصندوق أعلاه")
        else:
            st.warning("⚠️ لا توجد نتيجة للنسخ")


# ═══════════ التبويب الثاني ═══════════
with tab2:
    st.markdown("### 📄 تشكيل ملف نصي كامل")
    st.markdown("ارفع ملفاً نصياً (.txt) وسيتم تشكيله بالكامل")

    uploaded_file = st.file_uploader(
        "اختر ملفاً نصياً",
        type=["txt"],
        help="يدعم ملفات .txt بترميز UTF-8",
    )

    if uploaded_file is not None:
        file_content = uploaded_file.read().decode("utf-8")
        st.text_area(
            "محتوى الملف:",
            value=file_content,
            height=150,
            disabled=True,
        )

        if st.button("✍️ تشكيل الملف بالكامل", type="primary"):
            with st.spinner("⏳ جاري تشكيل الملف..."):
                paragraphs = file_content.split("\n")
                results = []
                progress_bar = st.progress(0)

                for i, para in enumerate(paragraphs):
                    if para.strip():
                        r = diacritizer.quick_tashkeel(para)
                        results.append(r)
                    else:
                        results.append("")
                    progress_bar.progress(
                        (i + 1) / len(paragraphs)
                    )

                full_result = "\n".join(results)
                progress_bar.empty()

            st.markdown("### ✨ النتيجة:")
            st.text_area(
                "النص المشكل:",
                value=full_result,
                height=200,
            )

            st.download_button(
                label="💾 تحميل النتيجة",
                data=full_result.encode("utf-8"),
                file_name=f"tashkeel_{uploaded_file.name}",
                mime="text/plain",
            )


# ═══════════ التبويب الثالث ═══════════
with tab3:
    st.markdown("### 📊 تحليل النص")
    st.markdown("أدخل نصاً لتحليل بنيته وتشكيله")

    analysis_text = st.text_area(
        "النص للتحليل:",
        height=150,
        placeholder="أدخل نصاً عربياً مشكلاً أو غير مشكل...",
    )

    if st.button("📊 تحليل", type="primary"):
        if analysis_text.strip():
            # تشكيل
            result = diacritizer.process_text(analysis_text)

            if result["success"]:
                st.markdown("#### النص المشكل:")
                st.markdown(
                    f'<div class="diacritized-output">'
                    f'{result["diacritized"]}</div>',
                    unsafe_allow_html=True,
                )

                st.markdown("#### الإحصائيات:")
                stats = result["stats"]

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("الكلمات", stats["words"])
                    st.metric(
                        "الحروف العربية", stats["arabic_chars"]
                    )
                with col2:
                    st.metric(
                        "الحركات المضافة",
                        stats["total_diacritics"],
                    )
                    st.metric(
                        "نسبة التغطية",
                        f'{stats["coverage"]}%',
                    )
            else:
                st.error(f'❌ {result["error"]}')
        else:
            st.warning("⚠️ الرجاء إدخال نص")


# ═══════════════════════════════════════════
#          الفوتر
# ═══════════════════════════════════════════
st.markdown("---")
st.markdown(
    """
<div class="footer">
    <p>✍️ <strong>مُشكِّل النصوص العربية</strong>
    | مبني على نموذج CATT للذكاء الاصطناعي</p>
    <p>صُنع بـ ❤️ للغة العربية</p>
</div>
""",
    unsafe_allow_html=True,
)
