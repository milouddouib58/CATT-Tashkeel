# ✍️ مُشكِّل النصوص العربية | Arabic Text Diacritizer

تطبيق ويب ذكي للتشكيل الآلي للنصوص العربية باستخدام نموذج **CATT** للذكاء الاصطناعي.

![Arabic Diacritizer](https://img.shields.io/badge/Language-Arabic-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange)

---

## 🌟 المميزات

- ✅ تشكيل آلي دقيق باستخدام نموذج CATT
- ✅ وضعان: **سريع** (EncoderOnly) و**دقيق** (EncoderDecoder)
- ✅ واجهة **Streamlit** عصرية وتفاعلية
- ✅ واجهة **Gradio** بديلة
- ✅ صفحة **ويب مستقلة** (HTML/CSS/JS)
- ✅ دعم معالجة الملفات النصية
- ✅ إحصائيات تفصيلية عن التشكيل
- ✅ إمكانية إزالة التشكيل
- ✅ نماذج نصية جاهزة للتجربة
- ✅ تصميم متجاوب (Responsive)

---

## 🚀 التثبيت السريع

```bash
# استنساخ المشروع
git clone https://github.com/milouddouib58/arabic-diacritizer.git
cd arabic-diacritizer

# تشغيل سكريبت الإعداد
chmod +x setup.sh
./setup.sh
أو يدوياً:
Bash

pip install -r requirements.txt
📖 التشغيل
1️⃣ Streamlit (الموصى به)
Bash

streamlit run app_streamlit.py
ثم افتح: http://localhost:8501

2️⃣ Gradio
Bash

python app_gradio.py
ثم افتح: http://localhost:7860

3️⃣ صفحة الويب المستقلة
افتح الملف web/index.html في المتصفح مباشرة.

⚠️ صفحة الويب تحتاج خادم Streamlit أو Gradio يعمل في الخلفية
للتشكيل الحقيقي. بدونه ستعمل بوضع تجريبي.

📁 هيكل المشروع
text

arabic-diacritizer/
├── app_streamlit.py       # تطبيق Streamlit
├── app_gradio.py          # تطبيق Gradio
├── diacritizer.py         # محرك التشكيل
├── requirements.txt       # المتطلبات
├── setup.sh               # سكريبت الإعداد
├── README.md              # التوثيق
├── .streamlit/
│   └── config.toml        # إعدادات Streamlit
└── web/
    └── index.html         # صفحة الويب المستقلة
🛠️ التقنيات المستخدمة
التقنية	الاستخدام
CATT	نموذج التشكيل (PyTorch)
Streamlit	واجهة المستخدم الرئيسية
Gradio	واجهة بديلة + API
HTML/CSS/JS	صفحة ويب مستقلة
Python 3.8+	لغة البرمجة
📊 لقطات الشاشة
واجهة Streamlit
تصميم عصري داكن مع ألوان ذهبية
تبويبات: تشكيل فوري، معالجة ملفات، تحليل
إحصائيات تفصيلية مع توزيع الحركات
صفحة الويب
تصميم SPA (صفحة واحدة)
خلفية متحركة
تبويبات تفاعلية
نماذج جاهزة سريعة
🤝 المساهمة
المساهمات مرحب بها! يرجى:

عمل Fork للمشروع
إنشاء فرع جديد (git checkout -b feature/amazing)
عمل Commit (git commit -m 'إضافة ميزة رائعة')
دفع التغييرات (git push origin feature/amazing)
فتح Pull Request
📄 الرخصة
هذا المشروع مرخص تحت MIT License.

🙏 شكر وتقدير
نموذج CATT للتشكيل الآلي
مجتمع المصادر المفتوحة العربي
<div align="center"> <p>صُنع بـ ❤️ للغة العربية</p> </div> ```
🔧 طريقة التشغيل
Bash

# 1. استنساخ المشروع وتثبيت المتطلبات
pip install -r requirements.txt

# 2. تشغيل Streamlit
streamlit run app_streamlit.py

# 3. أو تشغيل Gradio
python app_gradio.py

# 4. أو فتح صفحة الويب مباشرة
# افتح web/index.html في المتصفح
ملاحظة مهمة: صفحة الويب المستقلة (web/index.html) تحاول الاتصال بخادم Streamlit أو Gradio. إذا لم يكن الخادم يعمل، ستعمل بوضع تجريبي محلي مع تشكيل عشوائي للعرض فقط. لتشكيل حقيقي يجب تشغيل أحد الخوادم أولاً.
