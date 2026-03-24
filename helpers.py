"""دوال مساعدة للتطبيق"""

import logging

logger = logging.getLogger(__name__)


def check_dependencies():
    """فحص المكتبات المثبتة"""
    libs = {
        "torch": "torch",
        "transformers": "transformers",
        "sentencepiece": "sentencepiece",
        "catt_tashkeel": "catt-tashkeel",
        "streamlit": "streamlit",
    }

    report = {}
    for module_name, pip_name in libs.items():
        try:
            mod = __import__(module_name)
            version = getattr(mod, "__version__", "مثبت")
            report[pip_name] = {"installed": True, "version": str(version)}
        except ImportError:
            report[pip_name] = {"installed": False, "version": None}

    return report


def do_tashkeel(text, engine):
    """
    تشكيل النص - حقيقي أو تجريبي

    إذا كان النموذج محمّلاً يستخدمه مباشرة
    وإلا يبحث في النماذج الجاهزة
    """
    from core.samples import DEMO_PAIRS

    # النموذج الحقيقي
    if engine.is_loaded:
        return engine.process_text(text)

    # الوضع التجريبي
    clean = engine.strip_diacritics(text.strip())

    # بحث مطابق
    if clean in DEMO_PAIRS:
        dia = DEMO_PAIRS[clean]
        return {
            "original": text,
            "diacritized": dia,
            "success": True,
            "processing_time": 0.001,
            "stats": engine.compute_stats(clean, dia),
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
                "stats": engine.compute_stats(key, val),
                "demo": True,
            }

    # لم يُعثر
    samples = "\n".join([f"• {k}" for k in list(DEMO_PAIRS.keys())[:5]])
    return {
        "original": text,
        "diacritized": "",
        "success": False,
        "error": (
            "⚡ **وضع تجريبي:** النص غير متوفر.\n\n"
            f"💡 **جرّب:**\n{samples}\n\n"
            "أو شغّل محلياً:\n"
            "```\npip install catt-tashkeel streamlit\n"
            "streamlit run app_streamlit.py\n```"
        ),
        "stats": {},
        "processing_time": 0,
    }
