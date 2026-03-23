"""
تطبيق Gradio المطور للتشكيل الآلي
"""

import gradio as gr
import logging
from diacritizer import ArabicDiacritizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# تحميل النموذج
diacritizer = ArabicDiacritizer(fast_mode=True)

# ═══════════════════════════════════════════
#            الدوال الرئيسية
# ═══════════════════════════════════════════

def tashkeel_text(text, mode):
    """تشكيل النص"""
    if mode == "إزالة التشكيل":
        return diacritizer.strip_diacritics(text), ""

    result = diacritizer.process_text(text)

    if result['success']:
        stats_text = (
            f"⏱️ الوقت: {result['processing_time']} ثانية\n"
            f"📝 الكلمات: {result['stats']['words']}\n"
            f"🔤 الحروف العربية: {result['stats']['arabic_chars']}\n"
            f"✍️ الحركات المضافة: {result['stats']['total_diacritics']}\n"
            f"📊 نسبة التغطية: {result['stats']['coverage']}%"
        )
        return result['diacritized'], stats_text
    else:
        return f"❌ {result['error']}", ""


def process_file(file):
    """معالجة ملف"""
    if file is None:
        return "الرجاء رفع ملف"

    content = open(file.name, 'r', encoding='utf-8').read()
    paragraphs = content.split('\n')
    results = []

    for para in paragraphs:
        if para.strip():
            results.append(diacritizer.quick_tashkeel(para))
        else:
            results.append('')

    return '\n'.join(results)


# ═══════════════════════════════════════════
#            CSS مخصص
# ═══════════════════════════════════════════

custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Amiri&display=swap');

.gradio-container {
    font-family: 'Tajawal', sans-serif !important;
    max-width: 1100px !important;
    margin: auto !important;
}

textarea {
    font-family: 'Amiri', serif !important;
    font-size: 1.3rem !important;
    line-height: 2.2 !important;
    direction: rtl !important;
    text-align: right !important;
}

.main-title {
    text-align: center;
    background: linear-gradient(135deg, #1a1a2e, #0f3460);
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 1.5rem;
    color: #e9c46a;
}

.main-title h1 { color: #e9c46a !important; }
.main-title p { color: #a8dadc !important; }

footer { display: none !important; }
"""

# ═══════════════════════════════════════════
#            بناء الواجهة
# ═══════════════════════════════════════════

EXAMPLES = [
    ["بسم الله الرحمن الرحيم"],
    ["ان الذين امنوا وعملوا الصالحات كانت لهم جنات الفردوس نزلا"],
    ["انما الاعمال بالنيات وانما لكل امرئ ما نوى"],
    ["اللغة العربية من اجمل اللغات واكثرها ثراء"],
    ["من جد وجد ومن زرع حصد"],
]

with gr.Blocks(
    title="مُشكِّل النصوص العربية | CATT",
    css=custom_css,
    theme=gr.themes.Soft()
) as demo:

    # العنوان
    gr.HTML("""
    <div class="main-title">
        <h1>✍️ مُشكِّل النصوص العربية</h1>
        <p>تشكيل آلي ذكي باستخدام نموذج CATT للذكاء الاصطناعي</p>
    </div>
    """)

    # حالة النموذج
    if diacritizer.is_loaded:
        gr.Markdown(f"✅ **النموذج جاهز** | {diacritizer.model_type}")
    else:
        gr.Markdown("❌ **فشل تحميل النموذج**")

    with gr.Tabs():
        # ═══════ تبويب التشكيل الفوري ═══════
        with gr.TabItem("✍️ تشكيل فوري"):
            with gr.Row():
                with gr.Column():
                    input_text = gr.Textbox(
                        lines=8,
                        placeholder="أدخل النص العربي هنا...",
                        label="📝 النص الأصلي",
                        rtl=True
                    )
                    mode = gr.Radio(
                        choices=["تشكيل", "إزالة التشكيل"],
                        value="تشكيل",
                        label="الوضع"
                    )

                with gr.Column():
                    output_text = gr.Textbox(
                        lines=8,
                        label="✨ النص المُشكَّل",
                        rtl=True,
                        interactive=False
                    )
                    stats_text = gr.Textbox(
                        lines=5,
                        label="📊 الإحصائيات",
                        interactive=False
                    )

            with gr.Row():
                tashkeel_btn = gr.Button(
                    "✍️ تشكيل", variant="primary", scale=2
                )
                clear_btn = gr.ClearButton(
                    [input_text, output_text, stats_text],
                    value="🗑️ مسح"
                )

            tashkeel_btn.click(
                fn=tashkeel_text,
                inputs=[input_text, mode],
                outputs=[output_text, stats_text]
            )

            gr.Examples(
                examples=EXAMPLES,
                inputs=input_text,
                label="📌 نماذج جاهزة"
            )

        # ═══════ تبويب معالجة الملفات ═══════
        with gr.TabItem("📄 معالجة ملف"):
            file_input = gr.File(
                label="ارفع ملفاً نصياً (.txt)",
                file_types=['.txt']
            )
            file_output = gr.Textbox(
                lines=10,
                label="النتيجة",
                rtl=True,
                interactive=False
            )
            file_btn = gr.Button("✍️ تشكيل الملف", variant="primary")
            file_btn.click(
                fn=process_file,
                inputs=file_input,
                outputs=file_output
            )

    # الفوتر
    gr.HTML("""
    <div style="text-align:center; padding:1.5rem; color:#666; margin-top:2rem;">
        <p>✍️ مُشكِّل النصوص العربية | نموذج CATT | صُنع بـ ❤️ للغة العربية</p>
    </div>
    """)


# ═══════════════════════════════════════════
#            التشغيل
# ═══════════════════════════════════════════
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    )
