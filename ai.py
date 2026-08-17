"""عميل Gemini لتوليد الردود العربية عند الحاجة."""

import google.generativeai as genai


class GeminiAssistant:
    def __init__(self, settings):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)

    def reply(self, message: str, memories: str = "", calendar_context: str = "") -> str:
        prompt = f"""
أنت مساعد شخصي عربي داخل تيليجرام. أجب بالعربية الفصحى المبسطة وباختصار مفيد.
لا تدّعِ تنفيذ إجراء لم يحدث. إذا كان طلب المستخدم متعلقاً بإضافة أو حذف موعد أو حفظ مهمة،
فسيعالجه التطبيق خارج النموذج. استخدم السياق التالي لتحسين الإجابة فقط.

ذاكرة المستخدم:
{memories or 'لا توجد ذاكرة محفوظة.'}

المواعيد القادمة:
{calendar_context or 'لا توجد مواعيد معروضة.'}

رسالة المستخدم:
{message}
"""
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.3, max_output_tokens=700),
        )
        return (response.text or "عذراً، لم أستطع تكوين رد الآن.").strip()
