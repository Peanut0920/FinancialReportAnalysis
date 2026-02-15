import os
import pandas as pd
import pytesseract
from PIL import Image
import cv2
import numpy as np

class DataLoader:
    """Handles loading financial data from various sources (images, CSV, Excel)."""
    
    @staticmethod
    def from_image(image_path):
        """
        Extract text from image using OCR with preprocessing.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Extracted text from the image
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise FileNotFoundError(f"Could not read image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get black text on white background
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            
            # Denoise
            denoised = cv2.medianBlur(thresh, 1)
            
            # Convert back to PIL for Tesseract
            pil_img = Image.fromarray(denoised)
            
            # Extract text with custom configuration for better table recognition
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$(),.- '
            text = pytesseract.image_to_string(pil_img, config=custom_config)
            
            return text
            
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return ""
    
    @staticmethod
    def from_csv(csv_path):
        """
        Load data from CSV file.
        
        Args:
            csv_path (str): Path to CSV file
            
        Returns:
            pd.DataFrame: Loaded data
        """
        try:
            return pd.read_csv(csv_path)
        except Exception as e:
            print(f"Error reading CSV {csv_path}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def from_excel(excel_path, sheet_name=0):
        """
        Load data from Excel file.
        
        Args:
            excel_path (str): Path to Excel file
            sheet_name (str/int): Sheet name or index
            
        Returns:
            pd.DataFrame: Loaded data
        """
        try:
            return pd.read_excel(excel_path, sheet_name=sheet_name)
        except Exception as e:
            print(f"Error reading Excel {excel_path}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def preprocess_text(text):
        """
        Clean and preprocess extracted text.
        
        Args:
            text (str): Raw text
            
        Returns:
            str: Cleaned text
        """
        # Remove extra whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
