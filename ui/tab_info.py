"""
تبويب المعلومات والتشخيص
يعرض: معلومات المشروع، حالة النظام، النماذج المتاحة
"""

import sys
import streamlit as st
from helpers import check_dependencies
from core.samples import DEMO_PAIRS


def render_tab_info(diacritizer, is_model_ok: bool):
    """
    عرض تبويب المعلومات

    المعاملات:
        diacritizer: كائن محرك التشكيل
        is_model_ok: هل النموذج محمل بنجاح
    """
    _render_about()
    st.markdown("---")
    _render_system_status(diacritizer, is_model_ok)

    if not is_model_ok:
        st.markdown("---")
        _render_demo_samples()


def _render_about():
    """عرض معلومات المشروع"""
    st.markdown("### ℹ️ حول المشروع")
    st.markdown("""
**مُشكِّل النصوص العربية** تطبيق ويب ذكي يستخدم نموذج
**CATT** *(Context-Aware Text Tashkeel)* المبني على تقنيات
التعلم العميق لإضافة الحركات تلقائياً على النصوص العربية.

---

#### ⚡ أوضاع العمل

| الوضع | الوصف | الاستخدام |
|-------|-------|-----------|
| **سريع** | EncoderOnly | استخدام عام سريع |
| **دقيق** | EncoderDecoder | نصوص تحتاج دقة عالية |
| **تجريبي** | نماذج جاهزة | عندما لا يتوفر النموذج |

---

#### 🚀 التشغيل المحلي
```bash
pip install catt-tashkeel streamlit torch transformers
streamlit run app_streamlit.py
