import random
import copy
from typing import Dict, Any, List

class ShuffleEngine:
    """
    Shuffles questions and option choices to generate distinct exam variants
    (Variant A, Variant B, etc.), preserving the correct answer associations.
    """

    @staticmethod
    def generate_variants(
        original_test_data: Dict[str, Any],
        shuffle_questions: bool,
        shuffle_options: bool,
        variants_count: int,
        questions_per_variant: int = None
    ) -> Dict[str, Any]:
        """
        Generates distinct test variants by shuffling questions and/or options.

        Args:
            original_test_data (dict): The original test data containing 'subject', 'topics', and 'questions'.
            shuffle_questions (bool): Whether to change the question ordering.
            shuffle_options (bool): Whether to change the options (A, B, C, D) ordering.
            variants_count (int): How many variants to generate (e.g. 2, 3, 4, 5).
            questions_per_variant (int): Optional number of questions to include per variant.

        Returns:
            dict: Structured variants data.
        """
        original_questions = original_test_data.get('questions', [])
        subject = original_test_data.get('subject', '')
        topics = original_test_data.get('topics', '')
        difficulty = original_test_data.get('difficulty', 'medium')
        language = original_test_data.get('language', 'uz')

        variants_list = []
        variant_identifiers = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

        for i in range(variants_count):
            var_char = variant_identifiers[i % len(variant_identifiers)]
            variant_name = f"Variant {var_char}"

            # Deep copy to avoid modifying original questions
            var_questions = copy.deepcopy(original_questions)

            # Shuffle the order of the questions if requested
            if shuffle_questions:
                # Use a specific seed for each variant to ensure randomness but reproducible per run if needed,
                # or standard random.shuffle. We use standard random.shuffle.
                random.shuffle(var_questions)

            # Limit the number of questions per variant if specified
            if questions_per_variant and 0 < questions_per_variant < len(var_questions):
                var_questions = var_questions[:questions_per_variant]

            # Process each question for option shuffling
            for q in var_questions:
                orig_options = q['options']
                orig_correct_key = q['answer']
                correct_option_text = orig_options[orig_correct_key]

                if shuffle_options:
                    # Convert options to a list of tuples (Key, Text)
                    opt_items = list(orig_options.items())
                    # Shuffle the items
                    random.shuffle(opt_items)

                    # Build new options mapping A, B, C, D
                    new_option_keys = ['A', 'B', 'C', 'D']
                    new_options = {}
                    new_correct_key = 'A'

                    for idx, (old_k, opt_text) in enumerate(opt_items):
                        new_k = new_option_keys[idx]
                        new_options[new_k] = opt_text
                        if opt_text == correct_option_text:
                            new_correct_key = new_k

                    q['options'] = new_options
                    q['answer'] = new_correct_key
                else:
                    # Keep original option layout, correct answer stays the same
                    pass

            variants_list.append({
                'name': variant_name,
                'questions': var_questions
            })

        return {
            'subject': subject,
            'topics': topics,
            'difficulty': difficulty,
            'language': language,
            'variants': variants_list,
            'shuffle_questions': shuffle_questions,
            'shuffle_options': shuffle_options,
            'questions_per_variant': questions_per_variant
        }
