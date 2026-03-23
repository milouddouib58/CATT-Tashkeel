"""
الوحدة الأساسية لمحرك التشكيل
تصدّر الكلاسات والبيانات الرئيسية
"""

from core.engine import ArabicDiacritizer
from core.samples import DEMO_PAIRS, SAMPLE_CATEGORIES

__all__ = [
    "ArabicDiacritizer",
    "DEMO_PAIRS",
    "SAMPLE_CATEGORIES",
]
