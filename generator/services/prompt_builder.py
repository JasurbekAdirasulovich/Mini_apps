class PromptBuilder:
    """
    Builds professional, structured prompts for Gemini API/other models 
    to generate multiple-choice questions matching specific parameters.
    """

    @staticmethod
    def build_prompt(
        subject: str,
        topics: str,
        count: int,
        difficulty: str,
        language: str
    ) -> str:
        """
        Builds the prompt string.

        Args:
            subject (str): Name of the course/subject.
            topics (str): Target topics.
            count (int): Number of questions.
            difficulty (str): 'easy', 'medium', or 'hard'.
            language (str): 'uz', 'ru', or 'en'.

        Returns:
            str: Generated prompt text.
        """
        # Map difficulty labels
        diff_labels = {
            'easy': 'Oson / Easy (boshlang\'ich tushunchalar va xotira)',
            'medium': 'O\'rta / Medium (tahliliy tushunchalar va tatbiq etish)',
            'hard': 'Qiyin / Hard (murakkab tahlil, sintez va muammolarni hal qilish)'
        }
        selected_diff = diff_labels.get(difficulty.lower(), 'O\'rta (Medium)')

        # Map language instructions
        lang_names = {
            'uz': 'O\'zbek tili (lotin alifbosida, rasmiy ilmiy-akademik tilda)',
            'ru': 'Rus tili (akademik tilda)',
            'en': 'Ingliz tili (akademik tilda)'
        }
        selected_lang = lang_names.get(language.lower(), 'O\'zbek tili')

        prompt = f"""Siz universitet professori, fan eksperti va testolog mutaxassisisiz.
        Sizning vazifangiz berilgan fan va mavzu(lar) asosida professional testlar yaratish.Testlar universitet darajasiga mos bo'lishi kerak.
        Noto'g'ri ma'lumot yozmang.Bilmagan ma'lumotni taxmin qilmang.Javoblar ilmiy jihatdan to'g'ri bo'lishi kerak.:

1. Fan nomi: {subject}
2. Qamrab olinadigan mavzular: {topics}
3. Testlar soni: {count} ta savol
4. Qiyinlik darajasi: {selected_diff}
5. Test tili: {selected_lang}

TEST SAVOLLARINI YARATISH BO'YICHA TALABLAR:
-Har bir savolda faqat bitta to'g'ri javob bo'lsin.
-Har bir savolda 4 ta variant bo'lsin.
-Variantlar mazmunan bir-biriga yaqin bo'lsin.
-"Hammasi to'g'ri" yoki "Hech biri" kabi javoblardan foydalanmang.
-Savollar takrorlanmasin.
-Savollar faqat berilgan mavzularga oid bo'lsin.
-Savollar nazariy va amaliy bilimni tekshirsin.
-To'g'ri javoblar A, B, C va D orasida tasodifiy joylashsin.
-Izoh yozmang.
-Kirish matni yozmang.
-Xulosa yozmang.
-Faqat JSON qaytaring.
-JSON tashqarisida hech qanday matn yozmang.
-Markdown ishlatmang.
-Kod bloklari ishlatmang.
-JSON sintaksisi to'g'ri bo'lishi shart.

SIZNING JAVOBINGIZ FAQAT VA FAQAT QUYIDAGI JSON FORMATIDA BO'LISHI SHART. HECH QANDAY KIRISH, TUSHUNTIRISH YOKI XULOSA YOZMANGLAR:

{{
  "questions": [
    {{
      "question": "Savol matni bu yerda yoziladi...",
      "options": {{
        "A": "A variantining matni",
        "B": "B variantining matni",
        "C": "C variantining matni",
        "D": "D variantining matni"
      }},
      "answer": "A"
    }}
  ]
}}
"""
        return prompt
