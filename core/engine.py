"""
محرك التشكيل الآلي للنصوص العربية
"""

import logging
import time
import re
import sys

logger = logging.getLogger(__name__)


class ArabicDiacritizer:
    """محرك التشكيل الرئيسي باستخدام CATT"""

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
        "[\u064B\u064C\u064D\u064E\u064F"
        "\u0650\u0651\u0652\u0670\u0640]"
    )
    ARABIC_PATTERN = re.compile(r"[\u0600-\u06FF]")
    DIACRITIC_PATTERN = re.compile(r"[\u064B-\u0652]")

    def __init__(self, fast_mode=True):
        self.fast_mode = fast_mode
        self.model = None
        self.is_loaded = False
        self.model_type = ""
        self.load_error = ""
        self._load_model()

    def _load_model(self):
        """تحميل النموذج"""
        logger.info("بدء تحميل نموذج CATT...")

        # فحص torch
        try:
            import torch
            logger.info("PyTorch: %s", torch.__version__)
        except ImportError:
            self.load_error = (
                "PyTorch غير مثبت.\n"
                "أضف torch إلى requirements.txt"
            )
            logger.error(self.load_error)
            return

        # فحص transformers
        try:
            import transformers
            logger.info("Transformers: %s", transformers.__version__)
        except ImportError:
            self.load_error = (
                "Transformers غير مثبت.\n"
                "أضف transformers إلى requirements.txt"
            )
            logger.error(self.load_error)
            return

        # تحميل CATT
        try:
            start = time.time()

            if self.fast_mode:
                from catt_tashkeel import CATTEncoderOnly
                self.model = CATTEncoderOnly()
                self.model_type = "EncoderOnly ⚡"
            else:
                from catt_tashkeel import CATTEncoderDecoder
                self.model = CATTEncoderDecoder()
                self.model_type = "EncoderDecoder 🎯"

            elapsed = time.time() - start
            logger.info("تم التحميل: %s (%.1fs)", self.model_type, elapsed)
            self.is_loaded = True

        except ImportError as e:
            self.load_error = f"catt-tashkeel غير مثبت: {e}"
            logger.error(self.load_error)
        except MemoryError:
            self.load_error = "ذاكرة غير كافية لتحميل النموذج"
            logger.error(self.load_error)
        except Exception as e:
            self.load_error = f"{type(e).__name__}: {e}"
            logger.error(self.load_error)

    def process_text(self, text):
        """تشكيل النص مع إحصائيات"""
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
            result["error"] = f"النموذج غير محمل: {self.load_error}"
            return result

        try:
            clean = self.strip_diacritics(text)
            start = time.time()
            diacritized = self.model.do_tashkeel(clean, verbose=False)
            elapsed = time.time() - start

            result["diacritized"] = diacritized
            result["success"] = True
            result["processing_time"] = round(elapsed, 3)
            result["stats"] = self.compute_stats(clean, diacritized)

        except Exception as e:
            logger.error("خطأ: %s", e)
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
        """إزالة الحركات"""
        if not text:
            return ""
        return self.STRIP_PATTERN.sub("", text)

    def compute_stats(self, original, diacritized):
        """حساب الإحصائيات"""
        arabic = len(self.ARABIC_PATTERN.findall(original))
        diac = len(self.DIACRITIC_PATTERN.findall(diacritized))
        words = len(original.split())

        breakdown = {}
        for char, name in self.HARAKAT.items():
            count = diacritized.count(char)
            if count > 0:
                breakdown[name] = count

        coverage = round(diac / arabic * 100, 1) if arabic > 0 else 0

        return {
            "arabic_chars": arabic,
            "total_diacritics": diac,
            "words": words,
            "coverage": coverage,
            "breakdown": breakdown,
        }
