import os
import re
import logging
import fitz
from docx import Document
from functools import wraps

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper

class DocumentHandler:
    def __init__(self, job_manager):
        self.job_manager = job_manager

    @handle_errors
    def process_documents(self):
        temp_dir = self.job_manager.job_data["Temp Dir"]
        for document in self.job_manager.job_data["Documents"]:
            path = document["Path"]
            alias = os.path.splitext(document["Alias"])[0]
            ext = document["Ext"]
            text = self.extract_text_from_file(path, ext)
            cleaned_text = self.clean_text(text)
            txt_path = os.path.join(temp_dir, alias + '.txt')
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(cleaned_text)
            document["Path"] = txt_path
            logging.info(f"Processed document: {document}")
        self.job_manager.update_status("Documents Processed")
        logging.info("Documents processed successfully")

    @handle_errors
    def extract_text_from_file(self, path, ext):
        parse_methods = {
            '.pdf': self.parse_pdf,
            '.docx': self.parse_docx,
            '.txt': self.parse_txt
        }
        if f".{ext}" in parse_methods:
            return parse_methods[f".{ext}"](path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    @handle_errors
    def parse_txt(self, path):
        with open(path, "r", encoding="utf-8") as file:
            return file.read()

    @handle_errors
    def parse_docx(self, path):
        doc = Document(path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    @handle_errors
    def parse_pdf(self, file_path):
        text = ""
        document = fitz.open(file_path)
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text += page.get_text()
        return text

    def clean_text(self, text):
        text = re.sub(r'[^\x20-\x7E]+', ' ', text)
        return text

    @handle_errors
    def load_text(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            logging.warning(f"UTF-8 decoding failed for {file_path}, trying ISO-8859-1 encoding")
            with open(file_path, 'r', encoding='ISO-8859-1') as file:
                return file.read()