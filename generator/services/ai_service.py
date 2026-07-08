import os
import logging
import requests
from typing import Dict, Any, Tuple

from .prompt_builder import PromptBuilder
from .response_parser import ResponseParser
from .json_validator import JSONValidator

logger = logging.getLogger(__name__)

class AIService:
    """
    Interface for communication with Cerebras Cloud API (primary) 
    and Groq Cloud API (secondary/fallback).
    """

    def __init__(self):
        self.cerebras_key = os.getenv('CEREBRAS_API_KEY', '').strip()
        self.groq_key = os.getenv('GROQ_API_KEY', '').strip()
        
        if not self.cerebras_key and not self.groq_key:
            raise ValueError(
                "CEREBRAS_API_KEY va GROQ_API_KEY topilmadi. "
                "Iltimos, .env faylida kamida bitta API kalitni sozlang."
            )

        self.cerebras_url = "https://api.cerebras.ai/v1/chat/completions"
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"

    def generate_test(
        self,
        subject: str,
        topics: str,
        count: int,
        difficulty: str,
        language: str,
        model_name: str = 'llama-3.1-8b-instant'
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Generates the multiple choice test.
        Tries Cerebras API first. If it fails, falls back to Groq API automatically.

        Returns:
            Tuple[bool, Dict[str, Any], str]: (Success, parsed_data_dict, warning/info message)
        """
        prompt = PromptBuilder.build_prompt(
            subject=subject,
            topics=topics,
            count=count,
            difficulty=difficulty,
            language=language
        )

        # 1. TRY CEREBRAS API FIRST
        if self.cerebras_key:
            logger.info("Attempting generation via Cerebras API...")
            
            # Map selected model to Cerebras models
            # Standardize model names for Cerebras API
            valid_cerebras_models = ['gemma-4-31b', 'zai-glm-4.7', 'gpt-oss-120b']
            cerebras_model = model_name
            if model_name not in valid_cerebras_models:
                cerebras_model = "gemma-4-31b"
            
            headers = {
                "Authorization": f"Bearer {self.cerebras_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": cerebras_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.3
            }

            try:
                response = requests.post(self.cerebras_url, headers=headers, json=payload, timeout=20)
                if response.status_code == 200:
                    response_json = response.json()
                    raw_text = response_json['choices'][0]['message']['content']
                    
                    parsed_data, parse_err = ResponseParser.parse_json(raw_text)
                    if not parse_err:
                        is_valid, val_err = JSONValidator.validate_test_data(parsed_data)
                        if is_valid:
                            return True, parsed_data, ""
                        else:
                            logger.warning(f"Cerebras response JSON schema error: {val_err}")
                    else:
                        logger.warning(f"Cerebras response parsing error: {parse_err}")
                else:
                    logger.warning(f"Cerebras API returned status {response.status_code}: {response.text}")
            except Exception as e:
                logger.warning(f"Cerebras API request failed: {str(e)}")

        # 2. FALLBACK TO GROQ API
        if self.groq_key:
            logger.info("Falling back to Groq API...")
            
            # Map Cerebras models to fallback Groq models
            groq_model = "llama-3.1-8b-instant"
            if model_name == "gpt-oss-120b":
                groq_model = "llama-3.1-70b-versatile"
            elif model_name == "zai-glm-4.7":
                groq_model = "mixtral-8x7b-32768"

            headers = {
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": groq_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.3
            }

            try:
                response = requests.post(self.groq_url, headers=headers, json=payload, timeout=20)
                if response.status_code == 200:
                    response_json = response.json()
                    raw_text = response_json['choices'][0]['message']['content']
                    
                    parsed_data, parse_err = ResponseParser.parse_json(raw_text)
                    if not parse_err:
                        is_valid, val_err = JSONValidator.validate_test_data(parsed_data)
                        if is_valid:
                            warning_msg = (
                                "Birlamchi Cerebras API xatolik berdi yoki limit tugadi. "
                                "Tizim zaxiradagi Groq API orqali testlarni muvaffaqiyatli yaratdi."
                            )
                            return True, parsed_data, warning_msg
                        else:
                            logger.error(f"Groq response JSON schema error: {val_err}")
                    else:
                        logger.error(f"Groq response parsing error: {parse_err}")
                else:
                    logger.error(f"Groq API returned status {response.status_code}: {response.text}")
            except Exception as e:
                logger.error(f"Groq API request failed: {str(e)}")

        # 3. BOTH FAILED
        error_msg = (
            "Testlarni yaratishda xatolik yuz berdi. Cerebras va Groq API kalitlari "
            "ishlamadi yoki limit tugagan bo'lishi mumkin."
        )
        return False, {}, error_msg
