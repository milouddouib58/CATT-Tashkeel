"""
✍️ مُشكِّل النصوص العربية - CATT Tashkeel
النسخة النهائية الكاملة - ملف واحد للنشر على Streamlit Cloud
"""

import streamlit as st
import logging
import time
import re
import sys

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
    """فحص جميع المكتبات وإرجاع تقرير مفصل"""
    report = {}
    libs = {
        "torch": "torch",
        "transformers": "transformers",
        "sentencepiece": "sentencepiece",
        "catt_tashkeel": "catt-tashkeel",
        "streamlit": "streamlit",
    }
    for module_name, pip_name in libs.items():
        try:
            mod = __import__(module_name)
            version = getattr(mod, "__version__", "مثبت")
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
    """محرك التشكيل الآلي للنصوص العربية باستخدام CATT"""

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
        """تحميل النموذج مع معالجة شاملة لجميع الأخطاء"""
        try:
            logger.info("=" * 50)
            logger.info("بدء تحميل نموذج CATT...")
            logger.info(f"Python: {sys.version}")
            logger.info(f"الوضع: {'سريع' if self.fast_mode else 'دقيق'}")

            # ── فحص PyTorch ──
            try:
                import torch
                logger.info(f"PyTorch: {torch.__version__}")
                logger.info(f"CUDA متاح: {torch.cuda.is_available()}")
            except ImportError:
                self.load_error = (
                    "مكتبة PyTorch غير مثبتة.\n\n"
                    "أضف هذا إلى requirements.txt:\n"
                    "```\n"
                    "--extra-index-url https://download.pytorch.org/whl/cpu\n"
                    "torch\n"
                    "```"
                )
                logger.error(self.load_error)
                return

            # ── فحص Transformers ──
            try:
                import transformers
                logger.info(f"Transformers: {transformers.__version__}")
            except ImportError:
                self.load_error = (
                    "مكتبة Transformers غير مثبتة.\n\n"
                    "أضف transformers إلى requirements.txt"
                )
                logger.error(self.load_error)
                return

            # ── تحميل CATT ──
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
                f"✅ تم التحميل بنجاح: {self.model_type} "
                f"({elapsed:.1f} ثانية)"
            )
            self.is_loaded = True

        except ImportError as e:
            self.load_error = (
                f"مكتبة catt-tashkeel غير مثبتة أو بها خلل.\n\n"
                f"الخطأ: {str(e)}\n\n"
                f"الحل: أضف catt-tashkeel إلى requirements.txt"
            )
            logger.error(self.load_error)

        except MemoryError:
            self.load_error = (
                "الذاكرة غير كافية لتحميل النموذج.\n\n"
                "Streamlit Cloud المجاني يوفر ~1GB فقط.\n"
                "الحل: شغّل التطبيق محلياً على جهازك."
            )
            logger.error(self.load_error)

        except RuntimeError as e:
            self.load_error = (
                f"خطأ في وقت التشغيل:\n{str(e)}\n\n"
                f"قد يكون السبب عدم توافق إصدارات المكتبات."
            )
            logger.error(self.load_error)

        except Exception as e:
            self.load_error = (
                f"خطأ غير متوقع: {type(e).__name__}\n"
                f"{str(e)}"
            )
            logger.error(self.load_error)

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

        if not self.is_loaded or self.model is None:
            result["error"] = f"النموذج غير محمل.\n{self.load_error}"
            return result

        try:
            clean = self.strip_diacritics(text)
            start = time.time()
            diacritized = self.model.do_tashkeel(clean, verbose=False)
            elapsed = time.time() - start

            result["diacritized"] = diacritized
            result["success"] = True
            result["processing_time"] = round(elapsed, 3)
            result["stats"] = self._get_stats(clean, diacritized)

        except Exception as e:
            logger.error(f"خطأ أثناء التشكيل: {e}")
            result["error"] = f"خطأ في التشكيل: {str(e)}"

        return result

    def quick_tashkeel(self, text):
        """تشكيل سريع يرجع النص المشكّل فقط"""
        if not text or not text.strip():
            return ""
        if not self.is_loaded or self.model is None:
            return "⚠️ النموذج غير جاهز"
        try:
            clean = self.strip_diacritics(text)
            return self.model.do_tashkeel(clean, verbose=False)
        except Exception as e:
            return f"❌ خطأ: {e}"

    def strip_diacritics(self, text):
        """إزالة جميع الحركات والتشكيل من النص"""
        return self.STRIP_PATTERN.sub("", text)

    def _get_stats(self, original, diacritized):
        """حساب إحصائيات التشكيل التفصيلية"""
        arabic_chars = len(re.findall(r"[\u0600-\u06FF]", original))
        diacritics_count = len(re.findall(r"[\u064B-\u0652]", diacritized))
        words = len(original.split())

        breakdown = {}
        for char, name in self.HARAKAT.items():
            c = diacritized.count(char)
            if c > 0:
                breakdown[name] = c

        coverage = 0
        if arabic_chars > 0:
            coverage = round(diacritics_count / arabic_chars * 100, 1)

        return {
            "arabic_chars": arabic_chars,
            "total_diacritics": diacritics_count,
            "words": words,
            "coverage": coverage,
            "breakdown": breakdown,
        }


# ═══════════════════════════════════════════════════
#         نماذج مُشكّلة مسبقاً (الوضع التجريبي)
# ═══════════════════════════════════════════════════
DEMO_PAIRS = {
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
    "اللغة العربية من اجمل اللغات واكثرها ثراء في المفردات والتراكيب": (
        "اللُّغَةُ الْعَرَبِيَّةُ مِنْ أَجْمَلِ اللُّغَاتِ "
        "وَأَكْثَرِهَا ثَرَاءً فِي الْمُفْرَدَاتِ وَالتَّرَاكِيبِ"
    ),
    "من جد وجد ومن زرع حصد ومن سار على الدرب وصل": (
        "مَنْ جَدَّ وَجَدَ وَمَنْ زَرَعَ حَصَدَ "
        "وَمَنْ سَارَ عَلَى الدَّرْبِ وَصَلَ"
    ),
    "فتح المسلمون الاندلس في عهد الدولة الاموية وازدهرت الحضارة الاسلامية فيها": (
        "فَتَحَ الْمُسْلِمُونَ الْأَنْدَلُسَ فِي عَهْدِ "
        "الدَّوْلَةِ الْأُمَوِيَّةِ وَازْدَهَرَتِ "
        "الْحَضَارَةُ الْإِسْلَامِيَّةُ فِيهَا"
    ),
    "العلم نور والجهل ظلام": (
        "الْعِلْمُ نُورٌ وَالْجَهْلُ ظَلَامٌ"
    ),
    "قل هو الله احد الله الصمد لم يلد ولم يولد": (
        "قُلْ هُوَ اللَّهُ أَحَدٌ اللَّهُ الصَّمَدُ "
        "لَمْ يَلِدْ وَلَمْ يُولَدْ"
    ),
    "طلب العلم فريضة على كل مسلم ومسلمة": (
        "طَلَبُ الْعِلْمِ فَرِيضَةٌ عَلَى كُلِّ مُسْلِمٍ وَمُسْلِمَةٍ"
    ),
    "الصبر مفتاح الفرج": (
        "الصَّبْرُ مِفْتَاحُ الْفَرَجِ"
    ),
}

SAMPLE_CATEGORIES = {
    "🕌 آيات قرآنية": [
        "بسم الله الرحمن الرحيم",
        "ان الذين امنوا وعملوا الصالحات كانت لهم جنات الفردوس نزلا",
        "قل هو الله احد الله الصمد لم يلد ولم يولد",
    ],
    "📜 أحاديث وحكم": [
        "انما الاعمال بالنيات وانما لكل امرئ ما نوى",
        "طلب العلم فريضة على كل مسلم ومسلمة",
        "الصبر مفتاح الفرج",
    ],
    "✨ أمثال": [
        "من جد وجد ومن زرع حصد ومن سار على الدرب وصل",
        "العلم نور والجهل ظلام",
    ],
    "📖 نصوص عامة": [
        "اللغة العربية من اجمل اللغات واكثرها ثراء في المفردات والتراكيب",
        "فتح المسلمون الاندلس في عهد الدولة الاموية وازدهرت الحضارة الاسلامية فيها",
    ],
}


# ═══════════════════════════════════════════════════
#              إعدادات صفحة Streamlit
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
CUSTOM_CSS = """
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
        padding-top: 1.5rem;
        max-width: 1200px;
    }

    /* ═══════ الهيدر ═══════ */
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
        position: relative;
        z-index: 1;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.4);
    }

    .hero p {
        color: #a8dadc !important;
        font-size: 1.1rem !important;
        margin-top: 0.5rem !important;
        position: relative;
        z-index: 1;
        font-weight: 300;
    }

    /* ═══════ مربعات النص ═══════ */
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

    /* ═══════ مربع النتيجة ═══════ */
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

    .result-box.empty-result {
        color: rgba(255,255,255,0.25);
        font-family: 'Tajawal', sans-serif !important;
        font-size: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* ═══════ بطاقات الإحصائيات ═══════ */
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

    /* ═══════ الأزرار ═══════ */
    .stButton > button {
        width: 100%;
        padding: 0.85rem 1.5rem !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }

    /* ═══════ شارات الحالة ═══════ */
    .badge-ok {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1.2rem;
        border-radius: 50px;
        font-size: 0.95rem;
        font-weight: 600;
        background: rgba(46,204,113,0.12);
        border: 1px solid rgba(46,204,113,0.3);
        color: #2ecc71;
    }

    .badge-demo {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1.2rem;
        border-radius: 50px;
        font-size: 0.95rem;
        font-weight: 600;
        background: rgba(243,156,18,0.12);
        border: 1px solid rgba(243,156,18,0.3);
        color: #f39c12;
    }

    .demo-notice {
        background: rgba(243,156,18,0.1);
        border: 1px solid rgba(243,156,18,0.25);
        color: #f39c12;
        padding: 0.8rem 1.2rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem 0;
        font-size: 0.95rem;
        direction: rtl;
    }

    /* ═══════ الشريط الجانبي ═══════ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg, #1a1a2e 0%, #16213e 100%
        ) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #e0e0e0 !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #e9c46a !important;
    }

    /* ═══════ جدول التشخيص ═══════ */
    .diag-tbl {
        width: 100%;
        border-collapse: collapse;
        direction: rtl;
        margin: 0.5rem 0;
    }

    .diag-tbl th, .diag-tbl td {
        padding: 0.5rem 0.8rem;
        text-align: right;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        font-size: 0.9rem;
    }

    .diag-tbl th { color: #e9c46a; font-weight: 700; }
    .clr-ok { color: #2ecc71; }
    .clr-fail { color: #e74c3c; }

    /* ═══════ الفوتر ═══════ */
    .app-footer {
        text-align: center;
        padding: 2rem 1rem;
        color: #555;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 3rem;
        font-size: 0.9rem;
    }

    .app-footer a {
        color: #e9c46a;
        text-decoration: none;
    }

    /* ═══════ إخفاء عناصر Streamlit ═══════ */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
#         تحميل النموذج مع التخزين المؤقت
# ═══════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def load_model(fast_mode=True):
    """تحميل النموذج مرة واحدة وتخزينه مؤقتاً"""
    return ArabicDiacritizer(fast_mode=fast_mode)


# ═══════════════════════════════════════════════════
#              دالة التشكيل الموحدة
# ═══════════════════════════════════════════════════
def do_tashkeel(text, engine):
    """
    تشكيل النص: إذا كان النموذج محملاً يستخدمه،
    وإلا يبحث في النماذج المُشكّلة مسبقاً
    """

    # ── الوضع الحقيقي ──
    if engine.is_loaded:
        return engine.process_text(text)

    # ── الوضع التجريبي ──
    clean = engine.strip_diacritics(text.strip())

    # بحث مطابق تماماً
    if clean in DEMO_PAIRS:
        dia = DEMO_PAIRS[clean]
        return {
            "original": text,
            "diacritized": dia,
            "success": True,
            "processing_time": 0.001,
            "stats": engine._get_stats(clean, dia),
            "demo": True,
        }

    # بحث جزئي
    for key, val in DEMO_PAIRS.items():
        if key in clean or clean in key:
            return {
                "original": text,
                "diacritized": val,
                "success": True,
                "processing_time": 0.001,
                "stats": engine._get_stats(key, val),
                "demo": True,
            }

    # لم يُعثر على تطابق
    available = "\n".join(
        [f"• {k}" for k in list(DEMO_PAIRS.keys())[:5]]
    )
    return {
        "original": text,
        "diacritized": "",
        "success": False,
        "error": (
            "⚡ **الوضع التجريبي:** هذا النص غير متوفر "
            "في النماذج الجاهزة.\n\n"
            "💡 **جرّب أحد هذه النصوص:**\n"
            f"{available}\n\n"
            "أو شغّل التطبيق **محلياً** لتشكيل أي نص:\n"
            "```\n"
            "pip install catt-tashkeel streamlit\n"
            "streamlit run app_streamlit.py\n"
            "```"
        ),
        "stats": {},
        "processing_time": 0,
    }


# ═══════════════════════════════════════════════════
#              الشريط الجانبي
# ═══════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ الإعدادات")
    st.markdown("---")

    # اختيار النموذج
    model_choice = st.radio(
        "🧠 نوع النموذج",
        ["سريع (EncoderOnly)", "دقيق (EncoderDecoder)"],
        index=0,
        help="السريع أقل استهلاكاً للذاكرة. الدقيق أعلى جودة.",
    )
    fast_mode = model_choice == "سريع (EncoderOnly)"

    st.markdown("---")
    st.markdown("## 📝 نماذج جاهزة")

    selected_sample = None
    for cat_name, cat_items in SAMPLE_CATEGORIES.items():
        st.markdown(f"**{cat_name}**")
        for sample_txt in cat_items:
            display_txt = (
                sample_txt[:30] + "..."
                if len(sample_txt) > 30
                else sample_txt
            )
            btn_key = f"sb_{hash(sample_txt)}"
            if st.button(
                display_txt,
                key=btn_key,
                use_container_width=True,
            ):
                selected_sample = sample_txt

    st.markdown("---")

    # أدوات إضافية
    st.markdown("## 🛠️ أدوات")
    strip_mode = st.checkbox("🔄 إزالة التشكيل", value=False)

    st.markdown("---")

    # تشخيص
    with st.expander("🔍 تشخيص المكتبات"):
        deps = check_dependencies()
        for lib_name, lib_info in deps.items():
            if lib_info["installed"]:
                st.markdown(
                    f"✅ **{lib_name}** `{lib_info['version']}`"
                )
            else:
                st.markdown(f"❌ **{lib_name}** غير مثبت")
        st.caption(
            f"Python {sys.version_info.major}."
            f"{sys.version_info.minor}."
            f"{sys.version_info.micro}"
        )

    st.markdown("---")
    st.markdown(
        "<p style='text-align:center; color:#555; "
        "font-size:0.75rem;'>صُنع بـ ❤️ للغة العربية</p>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════
#                الصفحة الرئيسية
# ═══════════════════════════════════════════════════

# ── الهيدر ──
st.markdown("""
<div class="hero">
    <span class="hero-icon">✍️</span>
    <h1>مُشكِّل النصوص العربية</h1>
    <p>تشكيل آلي ذكي باستخدام نموذج CATT للذكاء الاصطناعي</p>
</div>
""", unsafe_allow_html=True)


# ── تحميل النموذج ──
with st.spinner("🔄 جاري تحميل النموذج... قد يستغرق دقيقة أو أكثر"):
    diacritizer = load_model(fast_mode=fast_mode)

MODEL_OK = diacritizer.is_loaded
DEMO_MODE = not MODEL_OK

# ── عرض حالة النموذج ──
if MODEL_OK:
    st.markdown(
        f'<div class="badge-ok">'
        f"✅ النموذج جاهز &nbsp;|&nbsp; {diacritizer.model_type}"
        f"</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="badge-demo">'
        "⚡ وضع العرض التجريبي — نماذج مُشكّلة مسبقاً"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.expander("🔍 لماذا لم يُحمّل النموذج؟ (اضغط للتفاصيل)"):
        st.error(
            f"**السبب:**\n\n{diacritizer.load_error}"
        )
        st.markdown(
            "### 🛠️ الحل:\n\n"
            "**1. تأكد من ملف `requirements.txt`:**\n"
            "```\n"
            "--extra-index-url "
            "https://download.pytorch.org/whl/cpu\n"
            "torch\n"
            "torchaudio\n"
            "transformers\n"
            "sentencepiece\n"
            "protobuf\n"
            "catt-tashkeel\n"
            "streamlit\n"
            "```\n\n"
            "**2. أضف ملف `packages.txt`:**\n"
            "```\n"
            "build-essential\n"
            "libsndfile1\n"
            "```\n\n"
            "**3. أو شغّل محلياً:**\n"
            "```bash\n"
            "pip install catt-tashkeel streamlit\n"
            "streamlit run app_streamlit.py\n"
            "```"
        )

    st.markdown(
        '<div class="demo-notice">'
        "💡 جرّب النماذج الجاهزة من الشريط الجانبي. "
        "لتشكيل أي نص حر، شغّل التطبيق محلياً."
        "</div>",
        unsafe_allow_html=True,
    )

st.markdown("")

# ── تحديث الإدخال إذا ضُغط نموذج ──
if selected_sample is not None:
    st.session_state["input_text"] = selected_sample


# ═══════════════════════════════════════════════════
#                    التبويبات
# ═══════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(
    ["✍️ تشكيل فوري", "📄 معالجة ملف", "ℹ️ معلومات"]
)


# ═══════════════════════════════════
#       تبويب 1 — تشكيل فوري
# ═══════════════════════════════════
with tab1:
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
        )

        wc = len(input_text.split()) if input_text.strip() else 0
        cc = len(input_text)
        st.caption(f"📏 {wc} كلمة &nbsp;|&nbsp; {cc} حرف")

    with col_out:
        st.markdown("### ✨ النص المُشكَّل")
        out_holder = st.empty()
        out_holder.markdown(
            '<div class="result-box empty-result">'
            "سيظهر النص المُشكَّل هنا ⬇️"
            "</div>",
            unsafe_allow_html=True,
        )

    # ── أزرار التحكم ──
    bc1, bc2, bc3 = st.columns([3, 1, 1])

    with bc1:
        btn_label = "🔄 إزالة التشكيل" if strip_mode else "✍️ تشكيل النص"
        run_btn = st.button(
            btn_label, type="primary", use_container_width=True
        )

    with bc2:
        clr_btn = st.button("🗑️ مسح", use_container_width=True)

    with bc3:
        cpy_btn = st.button("📋 نسخ", use_container_width=True)

    # ── زر المسح ──
    if clr_btn:
        st.session_state["input_text"] = ""
        st.session_state["last_result"] = ""
        st.rerun()

    # ── زر التشكيل / الإزالة ──
    if run_btn and input_text.strip():

        # وضع إزالة التشكيل
        if strip_mode:
            stripped = diacritizer.strip_diacritics(input_text)
            out_holder.markdown(
                f'<div class="result-box">{stripped}</div>',
                unsafe_allow_html=True,
            )
            st.session_state["last_result"] = stripped
            st.success("✅ تمت إزالة التشكيل بنجاح")

        # وضع التشكيل
        else:
            with st.spinner("⏳ جاري التشكيل..."):
                result = do_tashkeel(input_text, diacritizer)

            if result["success"]:
                # عرض النتيجة
                out_holder.markdown(
                    f'<div class="result-box">'
                    f'{result["diacritized"]}</div>',
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

                # ═══ الإحصائيات ═══
                st.markdown("---")
                st.markdown("### 📊 إحصائيات التشكيل")

                stats = result["stats"]
                m1, m2, m3, m4 = st.columns(4)

                with m1:
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<span class="metric-val">{stats["words"]}</span>'
                        f'<span class="metric-lbl">كلمة</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with m2:
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<span class="metric-val">{stats["arabic_chars"]}</span>'
                        f'<span class="metric-lbl">حرف عربي</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with m3:
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<span class="metric-val">{stats["total_diacritics"]}</span>'
                        f'<span class="metric-lbl">حركة مُضافة</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with m4:
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<span class="metric-val">{result["processing_time"]}s</span>'
                        f'<span class="metric-lbl">وقت المعالجة</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                # توزيع الحركات
                bd = stats.get("breakdown", {})
                if bd:
                    st.markdown("#### 🔤 توزيع الحركات")
                    max_v = max(bd.values()) if bd else 1
                    for h_name, h_count in sorted(
                        bd.items(), key=lambda x: x[1], reverse=True
                    ):
                        pct = h_count / max_v if max_v else 0
                        ca, cb, cx = st.columns([1, 3, 0.5])
                        with ca:
                            st.markdown(
                                f"<span style='color:#a8dadc;'>"
                                f"{h_name}</span>",
                                unsafe_allow_html=True,
                            )
                        with cb:
                            st.progress(pct)
                        with cx:
                            st.markdown(f"**{h_count}**")

            else:
                st.warning(result["error"])

    elif run_btn:
        st.warning("⚠️ الرجاء إدخال نص عربي أولاً")

    # ── زر النسخ ──
    if cpy_btn:
        lr = st.session_state.get("last_result", "")
        if lr:
            st.code(lr, language=None)
            st.info("📋 حدّد النص من الصندوق أعلاه ثم Ctrl+C")
        else:
            st.warning("⚠️ لا توجد نتيجة للنسخ بعد")


# ═══════════════════════════════════
#       تبويب 2 — معالجة ملف
# ═══════════════════════════════════
with tab2:
    st.markdown("### 📄 تشكيل ملف نصي كامل")
    st.markdown("ارفع ملف `.txt` بترميز UTF-8")

    if DEMO_MODE:
        st.info(
            "⚡ معالجة الملفات تحتاج إلى النموذج الحقيقي.\n\n"
            "شغّل التطبيق **محلياً** لاستخدام هذه الميزة:\n"
            "```\n"
            "pip install catt-tashkeel streamlit\n"
            "streamlit run app_streamlit.py\n"
            "```"
        )
    else:
        uploaded = st.file_uploader(
            "اختر ملفاً نصياً",
            type=["txt"],
        )

        if uploaded is not None:
            content = uploaded.read().decode("utf-8")
            st.text_area(
                "المحتوى الأصلي:",
                value=content,
                height=150,
                disabled=True,
            )

            if st.button("✍️ تشكيل الملف بالكامل", type="primary"):
                with st.spinner("⏳ جاري تشكيل الملف..."):
                    lines = content.split("\n")
                    out_lines = []
                    bar = st.progress(0)

                    total = len(lines)
                    for i, line in enumerate(lines):
                        if line.strip():
                            out_lines.append(
                                diacritizer.quick_tashkeel(line)
                            )
                        else:
                            out_lines.append("")
                        bar.progress((i + 1) / total)

                    bar.empty()
                    full_result = "\n".join(out_lines)

                st.markdown("### ✨ النتيجة:")
                st.text_area(
                    "النص المشكل:",
                    value=full_result,
                    height=200,
                )

                st.download_button(
                    label="💾 تحميل النتيجة",
                    data=full_result.encode("utf-8"),
                    file_name=f"tashkeel_{uploaded.name}",
                    mime="text/plain",
                )


# ═══════════════════════════════════
#       تبويب 3 — معلومات
# ═══════════════════════════════════
with tab3:
    st.markdown("### ℹ️ حول المشروع")

    st.markdown("""
**مُشكِّل النصوص العربية** هو تطبيق ويب يستخدم نموذج
**CATT** *(Context-Aware Text Tashkeel)* المبني على تقنيات
التعلم العميق لإضافة الحركات على النصوص العربية تلقائياً.

---

#### ⚡ أوضاع العمل

| الوضع | الوصف | متى يُستخدم |
|-------|-------|-------------|
| **سريع** | EncoderOnly — خفيف وسريع | الاستخدام العام |
| **دقيق** | EncoderDecoder — أعلى جودة | نصوص تحتاج دقة عالية |
| **تجريبي** | نماذج جاهزة مُشكّلة | عندما لا يتوفر النموذج |

---

#### 🚀 التشغيل المحلي
```bash
pip install catt-tashkeel streamlit torch transformers
streamlit run app_streamlit.py
