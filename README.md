# وكيل الذكاء الاصطناعي الشخصي على تيليجرام

مشروع Python جاهز لبوت تيليجرام عربي يساعد المستخدم على حفظ المهام والملاحظات في SQLite، وإدارة مواعيد Google Calendar، والرد على الرسائل باستخدام Gemini، مع تذكير تلقائي قبل الموعد بساعة وملخص صباحي يومي.

> **تنبيه مهم بشأن الاستضافة المجانية:** تشغيل بوت تيليجرام بنظام polling يحتاج خدمة عاملة باستمرار. راجع خطة Railway الحالية قبل النشر؛ قد تتغير حدود الخطة المجانية أو تتطلب وسيلة دفع. قاعدة SQLite داخل الحاوية ليست تخزيناً دائماً بعد كل إعادة نشر، لذلك يوصى بإضافة Volume في Railway أو استبدال SQLite بقاعدة مستضافة إذا كانت البيانات مهمة.

## خيارات التشغيل

| الطريقة | المفاضلة | التكلفة | سهولة الإعداد |
|---|---|---|---|
| Railway Worker، وهو الخيار المطبق هنا | إعداد سريع ونشر من GitHub، لكن حدود الخطة المجانية والتخزين الدائم قد تتغير | مجانية ضمن الحدود الحالية أو حسب الخطة | سهلة |
| خادم VPS صغير أو خدمة Worker أخرى | تحكم أكبر وتخزين دائم أفضل، لكنه يحتاج إدارة خادم ومراقبة | غالباً مدفوعة شهرياً | متوسطة |

هذا المشروع يستخدم Railway لأنك طلبت ذلك، مع إبقاء الكود قابلاً للنقل إلى أي بيئة Python تدعم عملية عاملة مستمرة.

## المزايا

| الميزة | التنفيذ |
|---|---|
| محادثة عربية | Python Telegram Bot مع أوامر عربية ورسائل Gemini |
| Google Calendar | عرض وإضافة وحذف المواعيد عبر OAuth |
| الذاكرة | SQLite للمهام والملاحظات وحالة الإنجاز |
| المبادرة | تذكير كل ساعة بفحص المواعيد وملخص يومي في الوقت المحدد |
| الذكاء الاصطناعي | Gemini API عبر مكتبة Google الرسمية `google-genai` |
| النشر | Worker process عبر `Procfile` على Railway |

## المتطلبات

يحتاج المشروع إلى Python 3.11 أو أحدث، وحساب تيليجرام، وحساب Google، ومفتاح Gemini API. لا يحتاج المشروع إلى خادم ويب؛ فهو يعمل كعامل Worker ويتلقى رسائل تيليجرام عبر polling.

## 1. إنشاء البوت من BotFather

افتح تيليجرام وابحث عن [@BotFather](https://t.me/BotFather). أرسل الأمر `/newbot`، ثم اختر اسماً ظاهراً للبوت واسم مستخدم ينتهي بـ `bot`. سيعطيك BotFather رمزاً بالشكل `123456789:ABC...`؛ احفظه سرياً وضعه في المتغير `TELEGRAM_BOT_TOKEN`.

بعد تشغيل البوت، أرسل له `/start`. لمعرفة معرّف حسابك الرقمي، استخدم بوتاً موثوقاً مثل [@userinfobot](https://t.me/userinfobot)، ثم ضع الرقم في `ALLOWED_USER_IDS`. يفضل وضع المعرّف لحماية البوت؛ ترك المتغير فارغاً يسمح لأي شخص بالوصول إليه.

## 2. إنشاء مشروع Google Calendar API

افتح [Google Cloud Console](https://console.cloud.google.com/)، وأنشئ مشروعاً جديداً أو اختر مشروعاً موجوداً. من **APIs & Services > Library** فعّل **Google Calendar API**. بعد ذلك افتح شاشة موافقة OAuth من **Google Auth Platform**، وأضف بريدك الإلكتروني كمستخدم اختباري إذا كان التطبيق في وضع Testing.

من **Credentials > Create Credentials > OAuth client ID** اختر **Desktop app**، ثم نزّل ملف JSON. أعد تسمية الملف إلى `credentials.json` وضعه مؤقتاً في مجلد المشروع. تتبع هذه الخطوة تدفق OAuth الرسمي لتطبيق Python المكتبي.[1]

ثبّت الاعتمادات وشغّل التفويض مرة واحدة محلياً:

```bash
python -m venv .venv
source .venv/bin/activate       # على Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python scripts/authorize_calendar.py
```

ستفتح نافذة المتصفح لتسجيل الدخول والموافقة. بعد النجاح سيُنشأ `token.json`. لا ترفع `credentials.json` أو `token.json` إلى GitHub. في Railway انسخ محتوى كل ملف إلى المتغير المقابل، أو استخدم الطريقة الأسهل التالية:

```bash
python -c "import json; print(json.dumps(json.load(open('credentials.json')), separators=(',', ':')))"
python -c "import json; print(json.dumps(json.load(open('token.json')), separators=(',', ':')))"
```

ضع الناتج الأول في `GOOGLE_CREDENTIALS_JSON` والثاني في `GOOGLE_TOKEN_JSON`. إذا انتهت صلاحية رمز التحديث أو ألغيت الصلاحية، أعد تشغيل سكربت التفويض وارفع محتوى `token.json` الجديد.

## 3. الحصول على مفتاح Gemini المجاني

افتح [Google AI Studio](https://aistudio.google.com/app/apikey)، وسجّل الدخول بحساب Google، ثم اختر **Create API key**. انسخ المفتاح إلى `GEMINI_API_KEY`. قد تتغير حدود الاستخدام المجاني والنماذج المتاحة حسب البلد والحساب؛ راجع صفحة التسعير والحصص قبل الاستخدام الإنتاجي. يمكن تغيير اسم النموذج من `GEMINI_MODEL` إذا لم يكن النموذج الافتراضي متاحاً في حسابك.

## 4. الإعداد والتشغيل محلياً

انسخ ملف البيئة النموذجي:

```bash
cp .env.example .env
```

املأ `TELEGRAM_BOT_TOKEN` و`GEMINI_API_KEY` وبيانات Google. للاختبار الأولي، اترك `GOOGLE_TOKEN_JSON` فارغاً إذا كان `token.json` موجوداً محلياً. حدّد المنطقة الزمنية المناسبة، مثل `Asia/Riyadh` أو `Asia/Dubai`، وحدد وقت الملخص في `DAILY_SUMMARY_TIME`.

شغّل البوت:

```bash
python app.py
```

ثم جرّب `/start` و`/addtask مراجعة العرض` و`/tasks` و`/events`. إضافة موعد تكون بهذا الشكل:

```text
/addevent اجتماع العميل | 2026-08-20 14:30 | 60
```

حيث الرقم الأخير مدة الموعد بالدقائق. حذف موعد يحتاج إلى المعرّف الذي يظهره الأمر `/events` أو بعد الإضافة:

```text
/deleteevent معرّف_الموعد
```

## 5. رفع المشروع إلى GitHub

أنشئ مستودعاً جديداً، ثم من داخل مجلد المشروع نفّذ:

```bash
git init
git add .
git commit -m "إضافة وكيل تيليجرام الشخصي"
git branch -M main
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```

تأكد من أن `.env` و`credentials.json` و`token.json` غير موجودة في الملفات المرفوعة. ملف `.gitignore` الموجود في المشروع يمنعها عادةً.

## 6. النشر على Railway

افتح [Railway](https://railway.app/)، سجّل الدخول، واختر **New Project > Deploy from GitHub Repo**، ثم اختر مستودع المشروع. سيقرأ Railway `requirements.txt` ويستخدم أمر التشغيل الموجود في `Procfile`:

```text
worker: python app.py
```

من تبويب **Variables** أضف متغيرات `.env.example` الأساسية. يجب إضافة `TELEGRAM_BOT_TOKEN` و`GEMINI_API_KEY` و`GOOGLE_CREDENTIALS_JSON` و`GOOGLE_TOKEN_JSON` و`TIMEZONE` و`DAILY_SUMMARY_TIME`. لا تضع علامات اقتباس حول JSON؛ الصق JSON كسطر واحد صالح.

للحفاظ على SQLite، أضف Volume إلى الخدمة واجعل `DATABASE_PATH` يشير إلى مسار داخل الـ Volume، مثل `/data/assistant.sqlite3`. إذا لم تضف Volume فقد تُفقد البيانات عند إعادة إنشاء الحاوية. لا تحتاج إلى Domain أو منفذ HTTP لأن الخدمة Worker وليست Web Service.

بعد النشر، راقب **Deploy Logs**. عند ظهور `بدء تشغيل وكيل تيليجرام` جرّب إرسال `/start` للبوت. لا تشغّل نسختين من البوت في الوقت نفسه باستخدام نفس الرمز، لأن Telegram قد يوقف إحدى جلسات polling.

## جدولة التذكيرات

يفحص البوت المواعيد كل ساعة، ويرسل تذكيراً عندما يبدأ الموعد خلال نافذة تقارب ساعة. ويرسل الملخص اليومي إلى معرّفات `ALLOWED_USER_IDS` فقط في الوقت المحدد. لذلك يجب ملء هذا المتغير عند تفعيل الرسائل الاستباقية؛ لا يمكن للبوت إرسال رسالة إلى مستخدم لم يبدأ محادثة معه سابقاً.

## هيكل الملفات

| الملف | الغرض |
|---|---|
| `app.py` | نقطة التشغيل وربط المعالجات والجدولة |
| `config.py` | قراءة متغيرات البيئة |
| `db.py` | قاعدة SQLite للمهام والملاحظات |
| `calendar_service.py` | Google Calendar OAuth وعمليات CRUD |
| `ai.py` | استدعاء Gemini |
| `handlers.py` | أوامر ورسائل تيليجرام |
| `scheduler.py` | التذكير والملخص اليومي |
| `scripts/authorize_calendar.py` | إنشاء `token.json` محلياً |
| `requirements.txt` | الاعتمادات |
| `Procfile` | أمر تشغيل Railway |
| `.env.example` | نموذج المتغيرات |

## ملاحظات أمنية وتشغيلية

لا تشارك رمز البوت أو مفاتيح Google أو Gemini. حدّد `ALLOWED_USER_IDS`، واستخدم Volume أو قاعدة بيانات دائمة للبيانات المهمة. يطلب Google نطاق Calendar الكامل لأن المشروع ينفذ الإضافة والحذف، وليس القراءة فقط. يمكنك تضييق النطاق لاحقاً إذا أزلت وظائف التعديل.

إذا ظهرت رسالة تفيد بأن النموذج غير متاح، غيّر `GEMINI_MODEL` إلى نموذج متاح في [قائمة نماذج Gemini](https://ai.google.dev/gemini-api/docs/models). وإذا تعذر الوصول إلى التقويم، تحقق من تفعيل Calendar API ومن أن `GOOGLE_TOKEN_JSON` ناتج من نفس مشروع OAuth.

## مراجع

[1]: https://developers.google.com/workspace/calendar/api/quickstart/python "Google Calendar API: Python quickstart"
[2]: https://ai.google.dev/gemini-api/docs "Gemini API documentation"
[3]: https://docs.railway.com/ "Railway documentation"
[4]: https://core.telegram.org/bots/api "Telegram Bot API"
