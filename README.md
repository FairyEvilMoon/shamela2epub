# shamela2epub

<div dir="rtl">

## الشاملة إلى EPUB

**shamela2epub** أداة مفتوحة المصدر لتحويل كتب **مكتبة الشاملة الإصدار الرابع** إلى ملفات **EPUB** و **HTML** مناسبة للقراءة على KOReader وبرامج قراءة الكتب الإلكترونية.

هذه الأداة لا توزع الكتب ولا قواعد البيانات. هي تعمل فقط على نسخة الشاملة المحلية الموجودة على جهازك.

> هذا المشروع مستقل وغير تابع رسميًا لمشروع مكتبة الشاملة.

---

## الشكر والتقدير

جزى الله خيرًا القائمين على **مكتبة الشاملة** وكل من ساهم في جمع التراث الإسلامي وتنسيقه وإتاحته للباحثين والقراء.

هذا المشروع أداة مساعدة صغيرة للاستفادة من نسخة الشاملة الموجودة عند المستخدم وتحويلها إلى صيغة قراءة إلكترونية. الفضل بعد الله يعود إلى الجهد الكبير الذي بذله فريق الشاملة والمساهمون فيها.

المشروع مجاني ومفتوح المصدر، ويجوز لأي شخص استخدامه أو تطويره أو تعديله أو توزيعه وفق رخصة MIT.

---

## المميزات

- تصدير كتب الشاملة 4 إلى EPUB و HTML.
- دعم اللغة العربية واتجاه RTL.
- إنشاء فهرس داخلي للكتاب.
- الحفاظ على فواصل الصفحات العلمية مثل: `ج 1 / ص 3`.
- قراءة العناوين من فهرس الشاملة.
- قراءة النص من فهرس Lucene الخاص بالشاملة.
- قراءة بيانات الكتاب من `master.db`.
- محاولة استخراج الغلاف من `cover.db`.
- إنتاج ثلاث نسخ:
  - `original`: النص كما هو.
  - `expanded`: توسيع الرموز الخاصة مثل ﷺ إلى نص كامل.
  - `expanded-no-harakat`: توسيع الرموز وحذف التشكيل لتحسين البحث والقواميس.

---

## المتطلبات

- Python 3.10 أو أحدث.
- Java 17 أو أحدث.
- Maven.

سبب وجود Java هو أن الشاملة 4 تخزن النصوص داخل فهارس Lucene، وقراءة هذه الفهارس تكون أكثر استقرارًا عبر مكتبات Lucene الرسمية. أما بقية البرنامج فهو مكتوب بلغة Python.

---

## التثبيت

```powershell
pip install -r requirements.txt
pip install -e .
```

---

## الاستخدام

```powershell
python -m shamela2epub.cli export --library D:\shamela4 --book 4445 --out output
```

أو بعد إضافة مجلد سكربتات Python إلى PATH:

```powershell
shamela2epub export --library D:\shamela4 --book 4445 --out output
```

لإنشاء HTML فقط:

```powershell
python -m shamela2epub.cli export --library D:\shamela4 --book 4445 --out output --html-only
```

---

## كيف يعمل؟

يعتمد البرنامج على هذه المصادر من نسخة الشاملة المحلية:

| المصدر | الوظيفة |
|---|---|
| `database/master.db` | بيانات الكتاب العامة |
| `database/book/.../<bookId>.db` | خريطة الصفحات والعناوين |
| `database/store/page` | نص الصفحات |
| `database/store/title` | نص العناوين |
| `database/cover.db` | الأغلفة عند توفرها |

البرنامج لا يقرأ `database/store/book` لأن بعض نسخ الشاملة تستخدم فيه إصدار Lucene مختلفًا عن إصدار فهرس الصفحات، وهذا ليس ضروريًا للتصدير.

---

## ملاحظات

- الأداة لا تعدّل أي ملف من ملفات الشاملة.
- لا ترفع ملفات الشاملة أو الكتب المصدرة إلى المستودع.
- استخدم الأداة بما يوافق حقوق الكتب وشروط استخدامك.

</div>

---

## Shamela to EPUB

**shamela2epub** is an open-source tool for converting books from a local **Shamela 4** installation into **EPUB** and **HTML** files suitable for KOReader and other ebook readers.

This tool does not distribute books or databases. It only works with the user's own local Shamela installation.

> This project is independent and is not officially affiliated with the Shamela project.

## Acknowledgements

Many thanks to the **Shamela Library** team and everyone who contributed to collecting, organizing, and digitizing Islamic scholarly works.

This project is only a small companion utility for exporting books from a local Shamela installation. The real credit belongs to the people behind Shamela and its contributors.

The project is free and open source. Anyone may use, modify, improve, or redistribute it under the MIT License.

## Features

- Export Shamela 4 books to EPUB and HTML.
- Arabic RTL support.
- EPUB table of contents.
- Scholarly page separators such as `ج 1 / ص 3`.
- Reads headings from Shamela's title index.
- Reads page text from Shamela's Lucene page index.
- Reads metadata from `master.db`.
- Attempts to extract covers from `cover.db`.
- Generates three editions:
  - `original`: unchanged text.
  - `expanded`: expands special symbols such as ﷺ.
  - `expanded-no-harakat`: expands symbols and removes Arabic diacritics for easier dictionary lookup.

## Requirements

- Python 3.10+
- Java 17+
- Maven

Java is used only by a small helper that reads Shamela's Lucene page/title indexes with the official Lucene libraries. The main exporter is written in Python.

## Installation

```powershell
pip install -r requirements.txt
pip install -e .
```

## Usage

```powershell
python -m shamela2epub.cli export --library D:\shamela4 --book 4445 --out output
```

HTML only:

```powershell
python -m shamela2epub.cli export --library D:\shamela4 --book 4445 --out output --html-only
```

## Repository notes

Do not commit Shamela databases, exported books, or local output folders. They are ignored by `.gitignore`.
