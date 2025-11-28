"""
Advanced quiz solver utilities for handling complex data tasks
"""

import re
import json
import base64
import io
import requests
import pandas as pd
from typing import Optional, Any, List
from groq import Groq

class QuizSolver:
    """Advanced quiz solver with multiple task handlers"""
    
    def __init__(self, groq_api_key: str):
        self.groq_api_key = groq_api_key
        self.client = None
    
    def get_client(self):
        """Lazy load Groq client"""
        if self.client is None:
            self.client = Groq(api_key=self.groq_api_key)
        return self.client
    
    def extract_numbers(self, text: str) -> List[float]:
        """Extract all numbers from text"""
        return [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
    
    def download_file(self, url: str) -> Optional[bytes]:
        """Download file from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None
    
    def extract_pdf_text(self, pdf_content: bytes) -> str:
        """Extract text from PDF"""
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(pdf_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return ""
    
    def parse_csv_data(self, csv_content: bytes) -> pd.DataFrame:
        """Parse CSV data"""
        try:
            return pd.read_csv(io.BytesIO(csv_content))
        except Exception as e:
            print(f"Error parsing CSV: {e}")
            return pd.DataFrame()
    
    def analyze_data(self, query: str, data: str) -> str:
        """Use Groq to analyze data"""
        system_prompt = """You are an expert data analyst. 
Analyze the provided data and answer questions precisely.
Extract exact values when asked for calculations.
Return ONLY the final answer without explanations."""
        
        try:
            client = self.get_client()
            message = client.messages.create(
                model="mixtral-8x7b-32768",
                max_tokens=2048,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": f"Analyze this data:\n\n{data}\n\nQuestion: {query}"}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Error analyzing data: {e}")
            return ""
    
    def call_api(self, url: str, method: str = "GET", headers: dict = None) -> Optional[dict]:
        """Make API call and return JSON response"""
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, timeout=30)
            else:
                return None
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error calling API: {e}")
            return None
    
    def parse_answer(self, response: str, instruction: str) -> Any:
        """Parse LLM response to extract answer in correct format"""
        response = response.strip()
        
        # Boolean detection
        if any(word in instruction.lower() for word in ["true", "false", "yes", "no"]):
            return response.lower() in ["true", "yes", "1"]
        
        # Number detection
        if any(word in instruction.lower() for word in ["sum", "total", "count", "number", "calculate", "value"]):
            numbers = re.findall(r'-?\d+\.?\d*', response)
            if numbers:
                try:
                    # Try int first
                    return int(float(numbers[-1]))
                except ValueError:
                    pass
        
        # JSON detection
        if "{" in response and "}" in response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                pass
        
        # Base64 detection
        if response.startswith("data:") and ";" in response:
            return response
        
        return response
    
    def format_answer(self, answer: Any) -> Any:
        """Format answer for submission"""
        if isinstance(answer, bool):
            return answer
        elif isinstance(answer, (int, float)):
            return answer
        elif isinstance(answer, dict):
            return answer
        elif isinstance(answer, list):
            return answer
        else:
            return str(answer)
