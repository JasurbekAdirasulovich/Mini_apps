from django.test import SimpleTestCase
from generator.services.prompt_builder import PromptBuilder
from generator.services.response_parser import ResponseParser
from generator.services.json_validator import JSONValidator
from generator.services.ai_service import AIService

class TestPromptBuilder(SimpleTestCase):
    def test_build_prompt_contains_parameters(self):
        subject = "Informatika"
        topics = "Internet, Tarmoqlar"
        prompt = PromptBuilder.build_prompt(
            subject=subject,
            topics=topics,
            count=5,
            difficulty="medium",
            language="uz"
        )
        self.assertIn(subject, prompt)
        self.assertIn(topics, prompt)
        self.assertIn("5 ta savol", prompt)
        self.assertIn("JSON", prompt)

class TestResponseParser(SimpleTestCase):
    def test_parse_clean_json(self):
        raw = '{"questions": [{"question": "Q1", "options": {"A": "a", "B": "b", "C": "c", "D": "d"}, "answer": "A"}]}'
        parsed, err = ResponseParser.parse_json(raw)
        self.assertEqual(err, "")
        self.assertEqual(parsed["questions"][0]["question"], "Q1")

    def test_parse_markdown_wrapped_json(self):
        raw = 'Some text before\n```json\n{"questions": [{"question": "Q2", "options": {"A": "a", "B": "b", "C": "c", "D": "d"}, "answer": "B"}]}\n```\nSome text after'
        parsed, err = ResponseParser.parse_json(raw)
        self.assertEqual(err, "")
        self.assertEqual(parsed["questions"][0]["question"], "Q2")

class TestJSONValidator(SimpleTestCase):
    def test_valid_json_structure(self):
        data = {
            "questions": [
                {
                    "question": "Q1",
                    "options": {"A": "optA", "B": "optB", "C": "optC", "D": "optD"},
                    "answer": "A"
                }
            ]
        }
        is_valid, err = JSONValidator.validate_test_data(data)
        self.assertTrue(is_valid)
        self.assertEqual(err, "")

    def test_invalid_json_missing_keys(self):
        data = {
            "questions": [
                {
                    "question": "Q1",
                    "options": {"A": "optA", "B": "optB", "C": "optC"},  # Missing D
                    "answer": "A"
                }
            ]
        }
        is_valid, err = JSONValidator.validate_test_data(data)
        self.assertFalse(is_valid)
        self.assertIn("variantlar orasida 'D' varianti topilmadi", err)

from unittest.mock import patch, MagicMock

class TestAIService(SimpleTestCase):
    @patch('requests.post')
    @patch.dict('os.environ', {
        'CEREBRAS_API_KEY': 'mock-cerebras-key-2026',
        'GROQ_API_KEY': 'mock-groq-key-2026'
    })
    def test_cerebras_service_generation_success(self, mock_post):
        # Mock successful Cerebras response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"questions": [{"question": "Cerebras nima?", "options": {"A": "A", "B": "B", "C": "C", "D": "D"}, "answer": "A"}]}'
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        service = AIService()
        success, data, err = service.generate_test("Fizika", "Optika", 1, "medium", "uz")
        
        self.assertTrue(success)
        self.assertEqual(err, "")
        self.assertEqual(data["questions"][0]["question"], "Cerebras nima?")
        # Ensure only 1 post call was made (Cerebras), no fallback needed
        self.assertEqual(mock_post.call_count, 1)

    @patch('requests.post')
    @patch.dict('os.environ', {
        'CEREBRAS_API_KEY': 'mock-cerebras-key-2026',
        'GROQ_API_KEY': 'mock-groq-key-2026'
    })
    def test_cerebras_fails_falls_back_to_groq(self, mock_post):
        # Mock Cerebras failure (1st call) and Groq success (2nd call)
        mock_cerebras_response = MagicMock()
        mock_cerebras_response.status_code = 429
        
        mock_groq_response = MagicMock()
        mock_groq_response.status_code = 200
        mock_groq_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"questions": [{"question": "Groq nima?", "options": {"A": "A", "B": "B", "C": "C", "D": "D"}, "answer": "B"}]}'
                    }
                }
            ]
        }
        
        mock_post.side_effect = [mock_cerebras_response, mock_groq_response]
        
        service = AIService()
        success, data, err = service.generate_test("Fizika", "Optika", 1, "medium", "uz")
        
        self.assertTrue(success)
        self.assertIn("Groq API orqali testlarni muvaffaqiyatli yaratdi", err)
        self.assertEqual(data["questions"][0]["question"], "Groq nima?")
        # Ensure both calls were made
        self.assertEqual(mock_post.call_count, 2)

    @patch.dict('os.environ', {
        'CEREBRAS_API_KEY': '',
        'GROQ_API_KEY': ''
    })
    def test_both_apis_missing_error(self):
        with self.assertRaises(ValueError) as context:
            AIService()
        self.assertIn("topilmadi. Iltimos, .env faylida kamida bitta API kalitni sozlang", str(context.exception))

class TestShuffleEngine(SimpleTestCase):
    def test_variants_generation_count_and_structure(self):
        from generator.services.shuffle_engine import ShuffleEngine
        
        test_data = {
            'subject': 'Fizika',
            'topics': 'Optika',
            'difficulty': 'medium',
            'language': 'uz',
            'questions': [
                {
                    'question': 'Q1',
                    'options': {'A': 'optA', 'B': 'optB', 'C': 'optC', 'D': 'optD'},
                    'answer': 'A'
                },
                {
                    'question': 'Q2',
                    'options': {'A': 'optA2', 'B': 'optB2', 'C': 'optC2', 'D': 'optD2'},
                    'answer': 'B'
                }
            ]
        }
        
        variants = ShuffleEngine.generate_variants(
            original_test_data=test_data,
            shuffle_questions=True,
            shuffle_options=True,
            variants_count=3
        )
        
        self.assertEqual(variants['subject'], 'Fizika')
        self.assertEqual(len(variants['variants']), 3)
        
        # Test Variant A structure
        var_a = variants['variants'][0]
        self.assertEqual(var_a['name'], 'Variant A')
        self.assertEqual(len(var_a['questions']), 2)
        
        # Test correct answer option preservation
        # For each question in each variant, the option that corresponds to the correct answer
        # must have the same text as in the original questions.
        for var in variants['variants']:
            for q_var in var['questions']:
                # Find original question by text
                orig_q = next(oq for oq in test_data['questions'] if oq['question'] == q_var['question'])
                orig_correct_text = orig_q['options'][orig_q['answer']]
                
                # Check if correct answer option text matches
                new_correct_key = q_var['answer']
                new_correct_text = q_var['options'][new_correct_key]
                self.assertEqual(orig_correct_text, new_correct_text)

    def test_variants_generation_with_slicing(self):
        from generator.services.shuffle_engine import ShuffleEngine
        
        test_data = {
            'subject': 'Fizika',
            'topics': 'Optika',
            'difficulty': 'medium',
            'language': 'uz',
            'questions': [
                {'question': 'Q1', 'options': {'A': 'a', 'B': 'b', 'C': 'c', 'D': 'd'}, 'answer': 'A'},
                {'question': 'Q2', 'options': {'A': 'a', 'B': 'b', 'C': 'c', 'D': 'd'}, 'answer': 'B'},
                {'question': 'Q3', 'options': {'A': 'a', 'B': 'b', 'C': 'c', 'D': 'd'}, 'answer': 'C'}
            ]
        }
        
        variants = ShuffleEngine.generate_variants(
            original_test_data=test_data,
            shuffle_questions=True,
            shuffle_options=True,
            variants_count=2,
            questions_per_variant=2
        )
        
        self.assertEqual(len(variants['variants']), 2)
        # Check that each variant has exactly 2 questions instead of 3
        for var in variants['variants']:
            self.assertEqual(len(var['questions']), 2)


class TestExporter(SimpleTestCase):
    def setUp(self):
        self.variants_data = {
            'subject': 'Kalkulus',
            'topics': 'Limitlar, Hosilalar',
            'difficulty': 'medium',
            'language': 'uz',
            'variants': [
                {
                    'name': 'Variant A',
                    'questions': [
                        {
                            'question': 'Limit nima?',
                            'options': {'A': 'Opt A', 'B': 'Opt B', 'C': 'Opt C', 'D': 'Opt D'},
                            'answer': 'A'
                        }
                    ]
                },
                {
                    'name': 'Variant B',
                    'questions': [
                        {
                            'question': 'Limit nima?',
                            'options': {'A': 'Opt C', 'B': 'Opt A', 'C': 'Opt D', 'D': 'Opt B'},
                            'answer': 'B'
                        }
                    ]
                }
            ]
        }

    def test_word_exporter_generates_docx_bytes(self):
        from generator.services.word_exporter import WordExporter
        docx_stream = WordExporter.generate_docx(self.variants_data)
        
        # Docx file starts with the zip file signature PK\x03\x04
        bytes_data = docx_stream.getvalue()
        self.assertTrue(len(bytes_data) > 0)
        self.assertTrue(bytes_data.startswith(b'PK\x03\x04'))

    def test_pdf_exporter_generates_pdf_bytes(self):
        from generator.services.pdf_exporter import PDFExporter
        pdf_stream = PDFExporter.generate_pdf(self.variants_data)
        
        # PDF file starts with %PDF-
        bytes_data = pdf_stream.getvalue()
        self.assertTrue(len(bytes_data) > 0)
        self.assertTrue(bytes_data.startswith(b'%PDF-'))


