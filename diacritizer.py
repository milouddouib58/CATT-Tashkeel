"""
محرك التشكيل الآلي للنصوص العربية
يستخدم نموذج CATT للتشكيل بدقة عالية
"""

import logging
import time
import re
from typing import Optional, Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArabicDiacritizer:
    """محرك التشكيل الرئيسي"""

    # الحركات العربية
    DIACRITICS = {
        '\u064B': 'تنوين فتح',
        '\u064C': 'تنوين ضم',
        '\u064D': 'تنوين كسر',
        '\u064E': 'فتحة',
        '\u064F': 'ضمة',
        '\u0650': 'كسرة',
        '\u0651': 'شدة',
        '\u0652': 'سكون',
    }

    DIACRITIC_PATTERN = re.compile(
        '[\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0670]'
    )

    def __init__(self, fast_mode: bool = True):
        """
        تهيئة النموذج

        Args:
            fast_mode: True لاستخدام EncoderOnly (أسرع)
                      False لاستخدام EncoderDecoder (أدق)
        """
        self.fast_mode = fast_mode
        self.model = None
        self.is_loaded = False
        self._load_model()

    def _load_model(self):
        """تحميل النموذج"""
        try:
            logger.info("جاري تحميل نموذج CATT...")
            start_time = time.time()

            if self.fast_mode:
                from catt_tashkeel import CATTEncoderOnly
                self.model = CATTEncoderOnly()
                self.model_type = "EncoderOnly (سريع)"
            else:
                from catt_tashkeel import CATTEncoderDecoder
                self.model = CATTEncoderDecoder()
                self.model_type = "EncoderDecoder (دقيق)"

            elapsed = time.time() - start_time
            logger.info(f"تم تحميل النموذج {self.model_type} في {elapsed:.2f} ثانية")
            self.is_loaded = True

        except ImportError as e:
            logger.error(f"خطأ في استيراد المكتبة: {e}")
            logger.error("تأكد من تثبيت: pip install catt-tashkeel")
            self.is_loaded = False

        except Exception as e:
            logger.error(f"خطأ في تحميل النموذج: {e}")
            self.is_loaded = False

    def process_text(self, text: str) -> Dict:
        """
        تشكيل النص وإرجاع النتائج مع إحصائيات

        Args:
            text: النص العربي بدون تشكيل

        Returns:
            قاموس يحتوي على النص المشكل والإحصائيات
        """
        result = {
            'original': text,
            'diacritized': '',
            'success': False,
            'error': None,
            'stats': {},
            'processing_time': 0
        }

        # التحقق من النص
        if not text or not text.strip():
            result['error'] = "الرجاء إدخال نص عربي"
            return result

        if not self.is_loaded:
            result['error'] = "النموذج غير محمل. تأكد من تثبيت catt-tashkeel"
            return result

        try:
            # إزالة التشكيل الموجود مسبقاً
            clean_text = self.strip_diacritics(text)

            # التشكيل
            start_time = time.time()
            diacritized = self.model.do_tashkeel(clean_text, verbose=False)
            elapsed = time.time() - start_time

            # حساب الإحصائيات
            stats = self._calculate_stats(clean_text, diacritized)

            result['diacritized'] = diacritized
            result['success'] = True
            result['processing_time'] = round(elapsed, 3)
            result['stats'] = stats

        except Exception as e:
            logger.error(f"خطأ في التشكيل: {e}")
            result['error'] = str(e)

        return result

    def quick_tashkeel(self, text: str) -> str:
        """تشكيل سريع - يرجع النص المشكل فقط"""
        if not text or not text.strip():
            return ""
        if not self.is_loaded:
            return "⚠️ النموذج غير محمل"
        try:
            clean = self.strip_diacritics(text)
            return self.model.do_tashkeel(clean, verbose=False)
        except Exception as e:
            return f"❌ خطأ: {e}"

    def strip_diacritics(self, text: str) -> str:
        """إزالة جميع الحركات من النص"""
        return self.DIACRITIC_PATTERN.sub('', text)

    def _calculate_stats(self, original: str, diacritized: str) -> Dict:
        """حساب إحصائيات التشكيل"""
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', original))
        diacritics_added = len(re.findall(
            r'[\u064B-\u0652]', diacritized
        ))
        words = len(original.split())

        # عدد كل نوع من الحركات
        diacritic_counts = {}
        for d, name in self.DIACRITICS.items():
            count = diacritized.count(d)
            if count > 0:
                diacritic_counts[name] = count

        return {
            'arabic_chars': arabic_chars,
            'total_diacritics': diacritics_added,
            'words': words,
            'coverage': round(
                (diacritics_added / arabic_chars * 100), 1
            ) if arabic_chars > 0 else 0,
            'diacritic_breakdown': diacritic_counts
        }

    def batch_process(self, texts: List[str]) -> List[Dict]:
        """معالجة مجموعة من النصوص دفعة واحدة"""
        return [self.process_text(text) for text in texts]


# ===== للاختبار المباشر =====
if __name__ == "__main__":
    d = ArabicDiacritizer(fast_mode=True)
    test = "بسم الله الرحمن الرحيم"
    result = d.process_text(test)

    if result['success']:
        print(f"الأصلي: {result['original']}")
        print(f"المشكل: {result['diacritized']}")
        print(f"الوقت: {result['processing_time']} ثانية")
        print(f"الإحصائيات: {result['stats']}")
    else:
        print(f"خطأ: {result['error']}")
