"""
محرك التشكيل الآلي - مع معالجة شاملة للأخطاء
"""

import logging
import time
import re
import sys
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class ArabicDiacritizer:
    """محرك التشكيل الرئيسي مع معالجة أخطاء شاملة"""

    DIACRITICS_MAP = {
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
        self.fast_mode = fast_mode
        self.model = None
        self.is_loaded = False
        self.model_type = ""
        self.error_message = ""
        self._load_model()

    def _check_dependencies(self) -> Dict[str, bool]:
        """فحص جميع المتطلبات"""
        deps = {}

        # فحص PyTorch
        try:
            import torch
            deps['torch'] = True
            deps['torch_version'] = torch.__version__
            deps['cuda'] = torch.cuda.is_available()
            logger.info(f"PyTorch {torch.__version__} ✅")
        except ImportError:
            deps['torch'] = False
            logger.error("PyTorch غير مثبت ❌")

        # فحص transformers
        try:
            import transformers
            deps['transformers'] = True
            logger.info(f"Transformers {transformers.__version__} ✅")
        except ImportError:
            deps['transformers'] = False
            logger.error("Transformers غير مثبت ❌")

        # فحص sentencepiece
        try:
            import sentencepiece
            deps['sentencepiece'] = True
            logger.info("SentencePiece ✅")
        except ImportError:
            deps['sentencepiece'] = False
            logger.warning("SentencePiece غير مثبت ⚠️")

        # فحص catt_tashkeel
        try:
            import catt_tashkeel
            deps['catt_tashkeel'] = True
            logger.info("catt-tashkeel ✅")
        except ImportError:
            deps['catt_tashkeel'] = False
            logger.error("catt-tashkeel غير مثبت ❌")

        return deps

    def _load_model(self):
        """تحميل النموذج مع معالجة كل الأخطاء المحتملة"""
        logger.info("=" * 50)
        logger.info("فحص المتطلبات...")
        logger.info("=" * 50)

        # فحص المتطلبات أولاً
        deps = self._check_dependencies()

        # التحقق من المتطلبات الأساسية
        missing = []
        if not deps.get('torch'):
            missing.append('torch')
        if not deps.get('transformers'):
            missing.append('transformers')
        if not deps.get('catt_tashkeel'):
            missing.append('catt-tashkeel')

        if missing:
            self.error_message = (
                f"مكتبات مفقودة: {', '.join(missing)}\n"
                f"شغّل الأوامر التالية:\n"
            )
            for lib in missing:
                if lib == 'torch':
                    self.error_message += (
                        "pip install torch --index-url "
                        "https://download.pytorch.org/whl/cpu\n"
                    )
                else:
                    self.error_message += f"pip install {lib}\n"

            logger.error(self.error_message)
            self.is_loaded = False
            return

        # محاولة تحميل النموذج
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
                f"✅ تم تحميل {self.model_type} "
                f"في {elapsed:.1f} ثانية"
            )
            self.is_loaded = True
            self.error_message = ""

        except OSError as e:
            self.error_message = (
                f"خطأ في تحميل ملفات النموذج: {e}\n"
                "قد تحتاج اتصال إنترنت لتحميل الأوزان"
            )
            logger.error(self.error_message)

        except RuntimeError as e:
            error_str = str(e)
            if "CUDA" in error_str or "GPU" in error_str:
                self.error_message = (
                    "خطأ في GPU/CUDA. جرّب تثبيت نسخة CPU:\n"
                    "pip install torch --index-url "
                
