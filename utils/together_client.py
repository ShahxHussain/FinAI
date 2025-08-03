import os
import json
import base64
import streamlit as st
from typing import List, Optional, Dict, Tuple
from together import Together
import tempfile
import pytesseract
from PIL import Image
import io
import pdf2image
import PyPDF2
import csv

class TogetherClient:
    """Unified Together.ai client for all AI operations"""
    
    def __init__(self):
        api_key = st.secrets.get("TOGETHER_API_KEY")
        if not api_key:
            raise ValueError("TOGETHER_API_KEY not found in environment variables")
        self.client = Together(api_key=api_key)
        pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Update path as needed

    def _extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text directly from PDF without using OCR"""
        try:
            with io.BytesIO(pdf_bytes) as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                text = "\n".join([page.extract_text() for page in reader.pages])
                return text.strip() if text else ""
        except Exception as e:
            print(f"PDF text extraction error: {e}")
            return ""

    def _extract_text_from_image(self, image_bytes: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            return pytesseract.image_to_string(image)
        except Exception as e:
            print(f"Image OCR error: {e}")
            return ""

    def _process_csv_file(self, csv_bytes: bytes) -> List[Dict]:
        """Process a CSV file containing receipt data"""
        try:
            # Decode bytes to string
            csv_string = csv_bytes.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_string))
            
            results = []
            for row in csv_reader:
                # Check for different possible CSV formats
                if 'text' in row:
                    receipt_text = row['text']
                elif 'content' in row:
                    receipt_text = row['content']
                elif 'receipt_text' in row:
                    receipt_text = row['receipt_text']
                else:
                    # Use the first column if standard fields not found
                    receipt_text = list(row.values())[0]
                
                if receipt_text:
                    result = self.process_receipt(text=receipt_text)
                    results.append(result)
            
            return results
        
        except Exception as e:
            print(f"CSV processing error: {e}")
            return []

    def process_receipt(self, file_bytes: Optional[bytes] = None, text: str = "", file_type: str = None) -> Dict:
        """
        Process receipt from various formats with OCR fallback
        Supported file_types: 'pdf', 'image', 'text'
        """
        # Extract text from file if provided
        extracted_text = text
        if file_bytes and file_type:
            if file_type == 'pdf':
                extracted_text = self._extract_text_from_pdf(file_bytes)
                if not extracted_text:
                    return self._error_response("Failed to extract text from PDF")
            elif file_type in ['jpg', 'jpeg', 'png']:
                extracted_text = self._extract_text_from_image(file_bytes)
            elif file_type == 'txt':
                extracted_text = file_bytes.decode('utf-8', errors='ignore')
        
        # Prepare the prompt
        prompt = """Very carefully analyze this receipt and extract structured data. Follow these rules:

FIRST determine if this is actually a receipt (look for totals, items, prices, etc.)
If it's a receipt, extract these details with HIGH accuracy:
Analyze the receipt one by one and extract structured data for each of the receipts:
1. Total amount (with confidence score 0-1)
2. Merchant name (with confidence)
3. Transaction date (YYYY-MM-DD format)
4. Category (with confidence)
5. Line items (description, amount, quantity)

Categories: [Meals, Travel, Office, Software, Rent, Utilities, Other]

Respond with this exact JSON structure:
{
    "amount": {"value": float, "confidence": float},
    "merchant": {"value": str, "confidence": float},
    "date": {"value": str, "confidence": float},
    "category": {"value": str, "confidence": float},
    "description": str,
    "line_items": [
        {
            "description": str,
            "amount": float,
            "quantity": int
        }
    ]
}"""

        try:
            messages = [{
                "role": "user",
                "content": prompt + f"\n\nExtracted Receipt Text:\n{extracted_text}"
            }]

            # Include image data if available (for better accuracy)
            if file_bytes and file_type in ['jpg', 'jpeg', 'png']:
                encoded_image = base64.b64encode(file_bytes).decode('utf-8')
                messages.append({
                    "role": "user",
                    "content": f"data:image/{file_type};base64,{encoded_image}"
                })

            response = self.client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.1",
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"},
                max_tokens=2000
            )

            result = json.loads(response.choices[0].message.content)
            return self._validate_response(result, extracted_text)

        except Exception as e:
            print(f"Processing error: {e}")
            return self._error_response(extracted_text)

    def process_bulk_receipts(self, files: List[Tuple[bytes, str]] = None, texts: List[str] = None, csv_files: Optional[List[bytes]] = None, pdf_files: Optional[List[bytes]] = None) -> List[Dict]:
        """
        Process multiple receipts in bulk
        Args:
            files: List of tuples (file_bytes, file_type)
            texts: List of raw receipt texts
        Returns:
            List of processed receipt data
        """
        results = []
        
        # Process files
        if files:
            for file_bytes, file_type in files:
                try:   
                    result = self.process_receipt(file_bytes=file_bytes, file_type=file_type)
                    results.append(result)
                except Exception as e:
                    print(f"Failed to process file: {e}")
                    results.append(self._error_response("Processing failed"))
        
        # Process texts
        if texts:
            for text in texts:
                try:
                    if file_type == 'csv':
                        # Handle CSV files through the special processing
                        csv_results = self._process_csv_file(file_bytes)
                        results.extend(csv_results)
                    if file_type == 'pdf':
                        pdf_results = self.process_receipt(file_bytes=pdf_files, file_type='pdf')
                        results.append(pdf_results)
                    else:
                        result = self.process_receipt(text=text)
                        results.append(result)
                except Exception as e:
                    print(f"Failed to process text: {e}")
                    results.append(self._error_response("Processing failed"))
        
        return results

    def generate_text(self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000) -> str:
        """Generate text using Together.ai"""
        try:
            response = self.client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.1",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Text generation error: {e}")
            return ""

    def generate_json(self, prompt: str, temperature: float = 0.1) -> Dict:
        """Generate JSON response using Together.ai"""
        try:
            response = self.client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.1",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                response_format={"type": "json_object"},
                max_tokens=2000
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"JSON generation error: {e}")
            return {}

    def _validate_response(self, data: Dict, original_desc: str) -> Dict:
        """Ensure response meets expected format"""
        validated = {
            "amount": {"value": 0.0, "confidence": 0},
            "merchant": {"value": "", "confidence": 0},
            "date": {"value": "", "confidence": 0},
            "category": {"value": "Other", "confidence": 0},
            "description": original_desc[:200] if original_desc else "",
            "line_items": []
        }

        # Validate and copy valid fields
        if isinstance(data, dict):
            if "amount" in data and isinstance(data["amount"], dict):
                validated["amount"] = data["amount"]
            if "merchant" in data and isinstance(data["merchant"], dict):
                validated["merchant"] = data["merchant"]
            if "date" in data and isinstance(data["date"], dict):
                validated["date"] = data["date"]
            if "category" in data and isinstance(data["category"], dict):
                validated["category"] = data["category"]
            if "description" in data:
                validated["description"] = str(data["description"])
            if "line_items" in data and isinstance(data["line_items"], list):
                validated["line_items"] = data["line_items"]

        return validated

    def _error_response(self, description: str) -> Dict:
        """Generate error response"""
        return {
            "amount": {"value": 0.0, "confidence": 0},
            "merchant": {"value": "Unknown", "confidence": 0},
            "date": {"value": "", "confidence": 0},
            "category": {"value": "Other", "confidence": 0},
            "description": description,
            "line_items": []
        } 