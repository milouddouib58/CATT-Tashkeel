"""
✍️ مُشكِّل النصوص العربية - CATT Tashkeel
النسخة النهائية المُصلحة للنشر على Streamlit Cloud
"""

import streamlit as st
import logging
import time
import re
import sys
import os

# ═══════════════════════════════════════════════════
#                  إعداد السجلات
# ═══════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════
#              فحص المكتبات المطلوبة
# ═══════════════════════════════════════════════════
def check_dependencies():
    """فحص جميع المكتبات وإرجاع تقرير"""
    report = {}
    libs = {
        "torch": "torch",
        "transformers": "transformers",
        "sentencepiece": "sentencepiece",
        "catt_tashkeel": "catt-tashkeel",
    }
    for module_name, pip_name in libs.items():
        try:
            mod = __import__(module_name)
            version = getattr(mod, "__version__", "غير معروف")
            report[pip_name] = {
                "installed": True,
                "version": version,
            }
        except ImportError:
            report[pip_name] = {
                "installed": False,
                "version": None,
            }
    return report


# ═══════════════════════════════════════════════════
#              محرك التشكيل الرئيسي
# ═══════════════════════════════════════════════════
class ArabicDiacritizer:
    """محرك التشكيل الآلي للنصوص العربية"""

    HARAKAT = {
        "\u064B": "تنوين فتح",
        "\u064C": "تنوين ضم",
        "\u064D": "تنوين كسر",
        "\u064E": "فتحة",
        "\u064F": "ضمة",
        "\u0650": "كسرة",
        "\u0651": "شدة",
        "\u0652": "سكون",
    }

    STRIP_PATTERN = re.compile(
        "[\u064B-\u0652\u0670\u0640]"
    )

    def __init__(self, fast_mode=True):
        self.fast_mode = fast_mode
        self.model = None
        self.is_loaded = False
        self.model_type = ""
        self.load_error = ""
        self._load_model()

    def _load_model(self):
        """تحميل النموذج مع معالجة شاملة للأخطاء"""
        try:
            logger.info("=" * 50)
            logger.info("بدء تحميل نموذج CATT...")
            logger.info(f"Python: {sys.version}")

            # فحص torch أولاً
            try:
                import torch
                logger.info(f"PyTorch: {torch.__version__}")
                logger.info(
                    f"CUDA: {torch.cuda.is_available()}"
                )
                device = "cuda" if torch.cuda.is_available() else "cpu"
                logger.info(f"الجهاز: {device}")
            except ImportError:
                self.load_error = (
                    "مكتبة PyTorch غير مثبتة. "
                    "أضف torch إلى requirements.txt"
                )
                logger.error(self.load_error)
                return

            # فحص transformers
            try:
                import transformers
                logger.info(
                    f"Transformers: {transformers.__version__}"
                )
            except ImportError:
                self.load_error = (
                    "مكتبة Transformers غير مثبتة. "
                    "أضف transformers إلى requirements.txt"
                )
                logger.error(self.load_error)
                return

            # تحميل CATT
            start = time.time()

            if self.fast_mode:
                from catt_tashkeel import CATTEncoderOnly
                self.model = CATTEncoderOnly()
                self.model_type = "EncoderOnly ⚡ سريع"
            else:
                from catt_tashkeel import CATTEncoderDecoder
                self.model = CATTEncoderDecoder()
                self.model_type = "EncoderDecoder 🎯 دقيق"

            elapsed = time.time() - start
            logger.info(
                f"✅ تم التحميل: {self.model_type} "
                f"({elapsed:.1f}s)"
            )
            self.is_loaded = True

        except ImportError as e:
            self.load_error = (
                f"مكتبة catt-tashkeel غير مثبتة أو بها مشكلة.\n"
                f"التفاصيل: {str(e)}\n\n"
                f"الحل: تأكد من وجود السطر التالي في "
                f"requirements.txt:\n"
                f"catt-tashkeel"
            )
            logger.error(self.load_error)

        except MemoryError:
            self.load_error = (
                "ذاكرة غير كافية لتحميل النموذج.\n"
                "Streamlit Cloud المجاني يوفر 1GB فقط.\n"
                "جرب الترقية أو التشغيل محلياً."
            )
            logger.error(self.load_error)

        except Exception as e:
            self.load_error = (
                f"خطأ غير متوقع: {type(e).__name__}\n"
                f"{str(e)}"
            )
            logger.error(self.load_error)

    def process_text(self, text):
        """تشكيل النص مع إحصائيات كاملة"""
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
            result["error"] = (
                f"النموذج غير محمل.\n{self.load_error}"
            )
            return result

        try:
            clean = self.strip_diacritics(text)
            start = time.time()
            diacritized = self.model.do_tashkeel(
                clean, verbose=False
            )
            elapsed = time.time() - start

            result["diacritized"] = diacritized
            result["success"] = True
            result["processing_time"] = round(elapsed, 3)
            result["stats"] = self._get_stats(
                clean, diacritized
            )

        except Exception as e:
            logger.error(f"خطأ في التشكيل: {e}")
            result["error"] = str(e)

        return result

    def quick_tashkeel(self, text):
        """تشكيل سريع"""
        if not text or not text.strip():
            return ""
        if not self.is_loaded:
            return "⚠️ النموذج غير جاهز"
        try:
            clean = self.strip_diacritics(text)
            return self.model.do_tashkeel(clean, verbose=False)
        except Exception as e:
            return f"❌ {e}"

    def strip_diacritics(self, text):
        """إزالة التشكيل"""
        return self.STRIP_PATTERN.sub("", text)

    def _get_stats(self, original, diacritized):
        """حساب الإحصائيات"""
        ar = len(re.findall(r"[\u0600-\u06FF]", original))
        dr = len(re.findall(r"[\u064B-\u0652]", diacritized))
        words = len(original.split())

        breakdown = {}
        for char, name in self.HARAKAT.items():
            c = diacritized.count(char)
            if c > 0:
                breakdown[name] = c

        return {
            "arabic_chars": ar,
            "total_diacritics": dr,
            "words": words,
            "coverage": round(dr / ar * 100, 1) if ar else 0,
            "breakdown": breakdown,
        }


# ═══════════════════════════════════════════════════
#              نماذج مُشكّلة مسبقاً (للعرض)
# ═══════════════════════════════════════════════════
DEMO_SAMPLES = {
    "بسم الله الرحمن الرحيم": (
        "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ"
    ),
    "ان الذين امنوا وعملوا الصالحات كانت لهم جنات الفردوس نزلا": (
        "إِنَّ الَّذِينَ آمَنُوا وَعَمِلُوا الصَّالِحَاتِ "
        "كَانَتْ لَهُمْ جَنَّاتُ الْفِرْدَوْسِ نُزُلًا"
    ),
    "انما الاعمال بالنيات وانما لكل امرئ ما نوى": (
        "إِنَّمَا الْأَعْمَالُ بِالنِّيَّاتِ "
        "وَإِنَّمَا لِكُلِّ امْرِئٍ مَا نَوَى"
    ),
    "اللغة العربية من اجمل اللغات واكثرها ثراء": (
        "اللُّغَةُ الْعَرَبِيَّةُ مِنْ أَجْمَلِ اللُّغَاتِ "
        "وَأَكْثَرِهَا ثَرَاءً"
    ),
    "من جد وجد ومن زرع حصد ومن سار على الدرب وصل": (
        "مَنْ جَدَّ وَجَدَ وَمَنْ زَرَعَ حَصَدَ "
        "وَمَنْ سَارَ عَلَى الدَّرْبِ وَصَلَ"
    ),
    "فتح المسلمون الاندلس في عهد الدولة الاموية": (
        "فَتَحَ الْمُسْلِمُونَ الْأَنْدَلُسَ "
        "فِي عَهْدِ الدَّوْلَةِ الْأُمَوِيَّةِ"
    ),
    "العلم نور والجهل ظلام": (
        "الْعِلْمُ نُورٌ وَالْجَهْلُ ظَلَامٌ"
    ),
    "قل هو الله احد الله الصمد": (
        "قُلْ هُوَ اللَّهُ أَحَدٌ اللَّهُ الصَّمَدُ"
    ),
}

SAMPLE_CATEGORIES = {
    "🕌 آيات قرآنية": {
        "بسم الله الرحمن الرحيم",
        "ان الذين امنوا وعملوا الصالحات كانت لهم جنات الفردوس نزلا",
        "قل هو الله احد الله الصمد",
    },
    "📜 أحاديث": {
        "انما الاعمال بالنيات وانما لكل امرئ ما نوى",
    },
    "✨ حكم وأمثال": {
        "من جد وجد ومن زرع حصد ومن سار على الدرب وصل",
        "العلم نور والجهل ظلام",
    },
    "📖 نصوص عامة": {
        "اللغة العربية من اجمل اللغات واكثرها ثراء",
        "فتح المسلمون الاندلس في عهد الدولة الاموية",
    },
}


# ═══════════════════════════════════════════════════
#              إعدادات الصفحة
# ═══════════════════════════════════════════════════
st.set_page_config(
    page_title="مُشكِّل النصوص العربية | CATT",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ═══════════════════════════════════════════════════
#              أنماط CSS الكاملة
# ═══════════════════════════════════════════════════
st.markdown("""
<style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;900&display=swap'
    );
    @import url(
        'https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap'
    );

    :root {
        --gold: #e9c46a;
        --gold-dark: #d4a843;
        --cyan: #a8dadc;
        --dark1: #0a0a1a;
        --dark2: #1a1a2e;
        --dark3: #16213e;
        --dark4: #0f3460;
        --orange: #f4a261;
        --red: #e74c3c;
        --green: #2ecc71;
    }

    * { font-family: 'Tajawal', sans-serif !important; }

    .main .block-container {
        padding-top: 1.5rem;
        max-width: 1200px;
    }

    /* ═══ الهيدر ═══ */
    .hero {
        background: linear-gradient(
            135deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%
        );
        padding: 2.5rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.4);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(233,196,106,0.15);
    }

    .hero::before {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(
            ellipse at 30% 50%,
            rgba(233,196,106,0.06) 0%,
            transparent 60%
        );
    }

    .hero-icon {
        font-size: 3rem;
        display: block;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }

    .hero h1 {
        color: #e9c46a !important;
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        margin: 0 !important;
        position: relative; z-index: 1;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.4);
    }

    .hero p {
        color: #a8dadc !important;
        font-size: 1.1rem !important;
        margin-top: 0.5rem !important;
        position: relative; z-index: 1;
        font-weight: 300;
    }

    /* ═══ مربعات النص ═══ */
    .stTextArea textarea {
        font-family: 'Amiri', serif !important;
        font-size: 1.35rem !important;
        line-height: 2.2 !important;
        direction: rtl !important;
        text-align: right !important;
        border: 2px solid rgba(233,196,106,0.2) !important;
        border-radius: 15px !important;
        padding: 1.2rem !important;
        background: rgba(26,26,46,0.5) !important;
        color: #e0e0e0 !important;
        transition: all 0.3s ease !important;
    }

    .stTextArea textarea:focus {
        border-color: #e9c46a !important;
        box-shadow: 0 0 0 3px rgba(233,196,106,0.15) !important;
        background: rgba(26,26,46,0.8) !important;
    }

    .stTextArea textarea::placeholder {
        color: rgba(255,255,255,0.3) !important;
    }

    /* ═══ النتيجة ═══ */
    .result-box {
        background: linear-gradient(
            135deg,
            rgba(233,196,106,0.08),
            rgba(244,162,97,0.05)
        );
        border: 2px solid rgba(233,196,106,0.3);
        border-radius: 15px;
        padding: 1.8rem;
        direction: rtl;
        text-align: right;
        font-family: 'Amiri', serif !important;
        font-size: 1.5rem;
        line-height: 2.5;
        color: #e9c46a;
        min-height: 180px;
        box-shadow: 0 4px 20px rgba(233,196,106,0.08);
        word-wrap: break-word;
    }

    .result-box.empty {
        color: rgba(255,255,255,0.25);
        font-family: 'Tajawal', sans-serif !important;
        font-size: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* ═══ البطاقات ═══ */
    .metric-card {
        background: linear-gradient(135deg, #16213e, #1a1a2e);
        border-radius: 15px;
        padding: 1.3rem;
        text-align: center;
        border: 1px solid rgba(233,196,106,0.15);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(233,196,106,0.35);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }

    .metric-val {
        font-size: 2rem;
        font-weight: 900;
        color: #e9c46a;
        display: block;
    }

    .metric-lbl {
        font-size: 0.9rem;
        color: #a8dadc;
        margin-top: 0.2rem;
    }

    /* ═══ الأزرار ═══ */
    .stButton > button {
        width: 100%;
        padding: 0.85rem 1.5rem !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }

    /* ═══ حالة النموذج ═══ */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1.2rem;
        border-radius: 50px;
        font-size: 0.95rem;
        font-weight: 600;
    }

    .status-ok {
        background: rgba(46,204,113,0.12);
        border: 1px solid rgba(46,204,113,0.3);
        color: #2ecc71;
    }

    .status-demo {
        background: rgba(243,156,18,0.12);
        border: 1px solid rgba(243,156,18,0.3);
        color: #f39c12;
    }

    .status-err {
        background: rgba(231,76,60,0.12);
        border: 1px solid rgba(231,76,60,0.3);
        color: #e74c3c;
    }

    /* ═══ الشريط الجانبي ═══ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg, #1a1a2e 0%, #16213e 100%
        ) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label {
        color: #e0e0e0 !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #e9c46a !important;
    }

    /* ═══ التشخيص ═══ */
    .diag-table {
        width: 100%;
        border-collapse: collapse;
        direction: rtl;
    }

    .diag-table th,
    .diag-table td {
        padding: 0.6rem 1rem;
        text-align: right;
        border-bottom: 1px solid rgba(255,255,255,0.08);
    }

    .diag-table th {
        color: #e9c46a;
        font-weight: 700;
    }

    .diag-ok { color: #2ecc71; }
    .diag-fail { color: #e74c3c; }

    /* ═══ عام ═══ */
    .footer {
        text-align: center;
        padding: 2rem 1rem;
        color: #666;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 3rem;
    }

    #MainMenu, footer, header { visibility: hidden; }

    .demo-badge {
        background: rgba(243,156,18,0.15);
        border: 1px solid rgba(243,156,18,0.3);
        color: #f39c12;
        padding: 0.8rem 1.2rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem 0;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
#              تحميل النموذج مع التخزين المؤقت
# ═══════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def load_model(fast_mode=True):
    """تحميل النموذج مرة واحدة فقط"""
    return ArabicDiacritizer(fast_mode=fast_mode)


# ═══════════════════════════════════════════════════
#              الشريط الجانبي
# ═══════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ الإعدادات")
    st.markdown("---")

    # نوع النموذج
    model_choice = st.radio(
        "🧠 نوع النموذج",
        ["سريع (EncoderOnly)", "دقيق (EncoderDecoder)"],
        index=0,
        help=(
            "السريع: أقل استهلاكاً للذاكرة وأسرع\n"
            "الدقيق: أعلى دقة لكن أبطأ وأكثر استهلاكاً"
        ),
    )
    fast_mode = model_choice == "سريع (EncoderOnly)"

    st.markdown("---")
    st.markdown("## 📝 نماذج جاهزة")

    selected_sample = None
    for category, samples in SAMPLE_CATEGORIES.items():
        st.markdown(f"**{category}**")
        for sample_text in samples:
            short = (
                sample_text[:35] + "..."
                if len(sample_text) > 35
                else sample_text
            )
            if st.button(
                short,
                key=f"s_{hash(sample_text)}",
                use_container_width=True,
            ):
                selected_sample = sample_text

    st.markdown("---")

    # أدوات
    st.markdown("## 🛠️ أدوات")
    strip_mode = st.checkbox(
        "🔄 وضع إزالة التشكيل", value=False
    )

    st.markdown("---")

    # التشخيص
    with st.expander("🔍 تشخيص المكتبات"):
        deps = check_dependencies()
        for lib, info in deps.items():
            if info["installed"]:
                st.markdown(
                    f"✅ **{lib}** → `{info['version']}`"
                )
            else:
                st.markdown(f"❌ **{lib}** → غير مثبت")

        st.markdown(f"**Python:** `{sys.version_info.major}."
                    f"{sys.version_info.minor}."
                    f"{sys.version_info.micro}`")

    st.markdown("---")
    st.markdown(
        "<p style='text-align:center; color:#555; "
        "font-size:0.8rem;'>صُنع بـ ❤️ للغة العربية</p>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════
#              الصفحة الرئيسية
# ═══════════════════════════════════════════════════

# الهيدر
st.markdown("""
<div class="hero">
    <span class="hero-icon">✍️</span>
    <h1>مُشكِّل النصوص العربية</h1>
    <p>تشكيل آلي ذكي باستخدام نموذج CATT للذكاء الاصطناعي</p>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
#              تحميل النموذج وتحديد الوضع
# ═══════════════════════════════════════════════════
with st.spinner("🔄 جاري تحميل النموذج... قد يستغرق دقيقة"):
    diacritizer = load_model(fast_mode=fast_mode)

# تحديد وضع العمل
USE_MODEL = diacritizer.is_loaded
DEMO_MODE = not USE_MODEL

if USE_MODEL:
    st.markdown(
        f'<div class="status-badge status-ok">'
        f"✅ النموذج جاهز | {diacritizer.model_type}"
        f"</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="status-badge status-demo">'
        "⚡ وضع العرض التجريبي (نماذج مُشكّلة مسبقاً)"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.expander("🔍 تفاصيل الخطأ وطريقة الإصلاح"):
        st.error(f"**سبب عدم تحميل النموذج:**\n\n"
                 f"{diacritizer.load_error}")
        st.markdown("---")
        st.markdown("### 🛠️ خطوات الإصلاح:")
        st.markdown("""
1. **تأكد من `requirements.txt`:**
