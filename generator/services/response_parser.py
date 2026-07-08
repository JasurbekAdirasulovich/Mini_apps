import json
import re
from typing import Dict, Any, Tuple

class ResponseParser:
    """
    Cleans and parses raw string response from AI model, 
    especially handling Markdown JSON block wrapping.
    """

    @staticmethod
    def parse_json(raw_text: str) -> Tuple[Dict[str, Any], str]:
        """
        Cleans Markdown format code blocks and parses JSON string.
        
        Args:
            raw_text (str): Raw model response string.
            
        Returns:
            Tuple[Dict[str, Any], str]: (Parsed dict or empty dict, Error description)
        """
        if not raw_text or not isinstance(raw_text, str):
            return {}, "Modeldan bo'sh yoki noto'g'ri turdagi javob olindi."

        cleaned = raw_text.strip()

        # Regular expression to extract JSON code block if wrapped in ```json ... ``` or ``` ... ```
        code_block_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', cleaned, re.IGNORECASE)
        
        if code_block_match:
            json_str = code_block_match.group(1)
        else:
            # If not wrapped, try to find the first '{' and last '}' and extract
            first_brace = cleaned.find('{')
            last_brace = cleaned.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_str = cleaned[first_brace:last_brace + 1]
            else:
                json_str = cleaned

        try:
            parsed_data = json.loads(json_str)
            return parsed_data, ""
        except json.JSONDecodeError as e:
            return {}, f"JSON formatida xatolik: {str(e)}. Manba matni: {raw_text[:200]}..."
