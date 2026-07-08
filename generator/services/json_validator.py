import json
from typing import Dict, Any, Tuple

class JSONValidator:
    """
    Validates that the JSON response from the AI model conforms to the expected 
    format for multiple-choice questions.
    """

    @staticmethod
    def validate_test_data(data: Any) -> Tuple[bool, str]:
        """
        Validates the structure of the parsed test data dictionary.
        
        Expected structure:
        {
            "questions": [
                {
                    "question": "string",
                    "options": {
                        "A": "string",
                        "B": "string",
                        "C": "string",
                        "D": "string"
                    },
                    "answer": "A" | "B" | "C" | "D"
                },
                ...
            ]
        }
        
        Returns:
            Tuple[bool, str]: (Is valid, Error message or empty string)
        """
        if not isinstance(data, dict):
            return False, "Javob JSON obyekti (dictionary) bo'lishi kerak."

        if 'questions' not in data:
            return False, "JSON tarkibida 'questions' kaliti topilmadi."

        questions = data['questions']
        if not isinstance(questions, list):
            return False, "'questions' kalitining qiymati massiv (list) bo'lishi kerak."

        if len(questions) == 0:
            return False, "'questions' massivi bo'sh bo'lmasligi kerak."

        for i, q in enumerate(questions):
            prefix = f"Savol {i+1}: "
            
            if not isinstance(q, dict):
                return False, f"{prefix}savol ma'lumotlari ob'ekt (dict) bo'lishi kerak."

            # Check question text
            if 'question' not in q or not q['question'] or not isinstance(q['question'], str):
                return False, f"{prefix}savol matni ('question') kiritilmagan yoki noto'g'ri shaklda."

            # Check options
            if 'options' not in q or not isinstance(q['options'], dict):
                return False, f"{prefix}variantlar ('options') ob'ekt (dict) ko'rinishida bo'lishi kerak."

            options = q['options']
            required_options = {'A', 'B', 'C', 'D'}
            
            # Check if all options exist and are non-empty strings
            for opt_key in required_options:
                if opt_key not in options:
                    return False, f"{prefix}variantlar orasida '{opt_key}' varianti topilmadi."
                if not options[opt_key] or not isinstance(options[opt_key], str):
                    return False, f"{prefix}'{opt_key}' variantining qiymati bo'sh yoki matn ko'rinishida emas."

            # Check for extra options to maintain standard A, B, C, D format
            if set(options.keys()) != required_options:
                return False, f"{prefix}faqat to'rtta variant bo'lishi kerak: A, B, C, D."

            # Check correct answer key
            if 'answer' not in q:
                return False, f"{prefix}to'g'ri javob kaliti ('answer') topilmadi."

            ans = q['answer']
            if ans not in required_options:
                return False, f"{prefix}to'g'ri javob kaliti ('answer') faqat 'A', 'B', 'C', 'D' qiymatlaridan biri bo'lishi kerak (Hozirgi: {ans})."

        return True, ""
