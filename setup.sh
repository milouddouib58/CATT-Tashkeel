#!/bin/bash

# ═══════════════════════════════════════════
#  سكريبت إعداد مشروع التشكيل الآلي
# ═══════════════════════════════════════════

echo "╔══════════════════════════════════════════╗"
echo "║   إعداد مشروع التشكيل الآلي للعربية    ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# 1. إنشاء بيئة افتراضية
echo "📦 إنشاء البيئة الافتراضية..."
python -m venv venv

# تفعيل البيئة
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "✅ تم تفعيل البيئة الافتراضية"

# 2. تثبيت المتطلبات
echo ""
echo "📥 تثبيت المتطلبات..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ تم تثبيت جميع المتطلبات"

# 3. إنشاء مجلدات
echo ""
echo "📂 إنشاء هيكل المشروع..."
mkdir -p .streamlit
mkdir -p static
mkdir -p web

echo "✅ تم إنشاء المجلدات"

# 4. عرض التعليمات
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║          الإعداد تم بنجاح! ✅           ║"
echo "╠══════════════════════════════════════════╣"
echo "║                                          ║"
echo "║  لتشغيل Streamlit:                      ║"
echo "║  streamlit run app_streamlit.py           ║"
echo "║                                          ║"
echo "║  لتشغيل Gradio:                         ║"
echo "║  python app_gradio.py                     ║"
echo "║                                          ║"
echo "║  لفتح صفحة الويب:                       ║"
echo "║  افتح web/index.html في المتصفح          ║"
echo "║                                          ║"
echo "╚══════════════════════════════════════════╝"
