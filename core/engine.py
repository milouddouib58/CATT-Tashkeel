"""
محرك التشكيل الآلي للنصوص العربية
يستخدم نموذج CATT (Context-Aware Text Tashkeel)

المسؤوليات:
    - تحميل نموذج CATT
    - تشكيل النصوص العربية
    - إزالة التشكيل
    - حساب الإحصائيات
"""

import logging
import time
import re
import sys

logger = logging.getLogger(__name__)


class ArabicDiacritizer:
    """
    محرك التشكيل الرئيسي

    يدعم وضعين:
        - سريع (EncoderOnly): أقل استهلاكاً للذاكرة وأسرع
        - دقيق (EncoderDecoder): أعلى دقة لكن أبطأ

    الاستخدام:
        >>> engine = ArabicDiacritizer(fast_mode=True)
        >>> result = engine.process_text("بسم الله الرحمن الرحيم")
        >>> print(result["diacritized"])
    """

    # ── خريطة الحركات العربية ──
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

    # ── نمط إزالة الحركات ──
    STRIP_PATTERN = re.compile(
        "[\u064B\u064C\u064D\u064E\u064F"
        "\u0650\u0651\u0652\u0670\u0640]"
    )

    # ── نمط اكتشاف الحروف العربية ──
    ARABIC_PATTERN = re.compile(r"[\u0600-\u06FF]")

    # ── نمط اكتشاف الحركات ──
    DIACRITIC_PATTERN = re.compile(r"[\u064B-\u0652]")

    def __init__(self, fast_mode: bool = True):
        """
        تهيئة محرك التشكيل

        المعاملات:
            fast_mode: True للوضع السريع، False للوضع الدقيق
        """
        self.fast_mode = fast_mode
        self.model = None
        self.is_loaded = False
        self.model_type = ""
        self.load_error = ""
        self._load_model()

    def _load_model(self):
        """تحميل النموذج مع معالجة شاملة لجميع الأخطاء المحتملة"""

        logger.info("=" * 50)
        logger.info("بدء تحميل نموذج CATT...")
        logger.info("Python: %s", sys.version)
        logger.info("الوضع: %s", "سريع" if self.fast_mode else "دقيق")

        # ── المرحلة 1: فحص PyTorch ──
        if not self._check_torch():
            return

        # ── المرحلة 2: فحص Transformers ──
        if not self._check_transformers():
            return

        # ── المرحلة 3: تحميل CATT ──
        self._load_catt()

    def _check_torch(self) -> bool:
        """فحص توفر PyTorch"""
        try:
            import torch

            logger.info("PyTorch: %s", torch.__version__)
            logger.info("CUDA متاح: %s", torch.cuda.is_available())
            return True

        except ImportError:
            self.load_error = (
                "مكتبة PyTorch غير مثبتة.\n\n"
                "أضف هذا إلى requirements.txt:\n"
                "```\n"
                "--extra-index-url "
                "https://download.pytorch.org/whl/cpu\n"
                "torch\n"
                "```"
            )
            logger.error("PyTorch غير مثبت")
            return False

    def _check_transformers(self) -> bool:
        """فحص توفر Transformers"""
        try:
            import transformers

            logger.info("Transformers: %s", transformers.__version__)
            return True

        except ImportError:
            self.load_error = (
                "مكتبة Transformers غير مثبتة.\n\n"
                "أضف transformers إلى requirements.txt"
            )
            logger.error("Transformers غير مثبت")
            return False

    def _load_catt(self):
        """تحميل نموذج CATT"""
        try:
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
                "✅ تم التحميل: %s (%.1f ثانية)",
                self.model_type, elapsed,
            )
            self.is_loaded = True

        except ImportError as exc:
            self.load_error = (
                f"مكتبة catt-tashkeel غير مثبتة أو بها خلل.\n\n"
                f"الخطأ: {exc}\n\n"
                f"الحل: أضف catt-tashkeel إلى requirements.txt"
            )
            logger.error("فشل استيراد catt-tashkeel: %s", exc)

        except MemoryError:
            self.load_error = (
                "الذاكرة غير كافية لتحميل النموذج.\n\n"
                "Streamlit Cloud المجاني يوفر ~1GB فقط.\n"
                "الحل: شغّل التطبيق محلياً على جهازك."
            )
            logger.error("ذاكرة غير كافية")

        except RuntimeError as exc:
            self.load_error = (
                f"خطأ في وقت التشغيل:\n{exc}\n\n"
                f"قد يكون السبب عدم توافق إصدارات المكتبات."
            )
            logger.error("RuntimeError: %s", exc)

        except Exception as exc:
            self.load_error = (
                f"خطأ غير متوقع: {type(exc).__name__}\n{exc}"
            )
            logger.error("خطأ غير متوقع: %s", exc)

    # ──────────────────────────────────────────
    #              واجهة التشكيل
    # ──────────────────────────────────────────

    def process_text(self, text: str) -> dict:
        """
        تشكيل النص مع إرجاع نتائج وإحصائيات مفصلة

        المعاملات:
            text: النص العربي المراد تشكيله

        القيمة المرجعة:
            قاموس يحتوي على:
                original, diacritized, success,
                error, stats, processing_time
        """
        result = {
            "original": text,
            "diacritized": "",
            "success": False,
            "error": None,
            "stats": {},
            "processing_time": 0,
        }

        # التحقق من النص
        if not text or not text.strip():
            result["error"] = "الرجاء إدخال نص عربي"
            return result

        # التحقق من النموذج
        if not self.is_loaded or self.model is None:
            result["error"] = (
                f"النموذج غير محمل.\n{self.load_error}"
            )
            return result

        # التشكيل
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
            result["stats"] = self._compute_stats(
                clean, diacritized
            )

        except Exception as exc:
            logger.error("خطأ أثناء التشكيل: %s", exc)
            result["error"] = f"خطأ في التشكيل: {exc}"

        return result

    def quick_tashkeel(self, text: str) -> str:
        """
        تشكيل سريع — يرجع النص المشكّل فقط بدون إحصائيات

        المعاملات:
            text: النص العربي

        القيمة المرجعة:
            النص المشكّل أو رسالة خطأ
        """
        if not text or not text.strip():
            return ""

        if not self.is_loaded or self.model is None:
            return "⚠️ النموذج غير جاهز"

        try:
            clean = self.strip_diacritics(text)
            return self.model.do_tashkeel(clean, verbose=False)
        except Exception as exc:
            return f"❌ خطأ: {exc}"

    def strip_diacritics(self, text: str) -> str:
        """إزالة جميع الحركات والتطويل من النص"""
        if not text:
            return ""
        return self.STRIP_PATTERN.sub("", text)

    # ──────────────────────────────────────────
    #              الإحصائيات
    # ──────────────────────────────────────────

    def _compute_stats(self, original: str, diacritized: str) -> dict:
        """
        حساب إحصائيات تفصيلية عن التشكيل

        المعاملات:
            original: النص الأصلي بدون حركات
            diacritized: النص بعد التشكيل

        القيمة المرجعة:
            قاموس إحصائيات
        """
        arabic_chars = len(self.ARABIC_PATTERN.findall(original))
        diacritics_count = len(
            self.DIACRITIC_PATTERN.findall(diacritized)
        )
        words = len(original.split())

        # توزيع الحركات
        breakdown = {}
        for char, name in self.HARAKAT.items():
            count = diacritized.count(char)
            if count > 0:
                breakdown[name] = count

        # نسبة التغطية
        coverage = 0.0
        if arabic_chars > 0:
            coverage = round(
                diacritics_count / arabic_chars * 100, 1
            )

        return {
            "arabic_chars": arabic_chars,
            "total_diacritics": diacritics_count,
            "words": words,
            "coverage": coverage,
            "breakdown": breakdown,
        }
