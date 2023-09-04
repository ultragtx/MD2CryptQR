from cryptography.fernet import Fernet
from pdf_writer import PDFWriter
from markdown_parser import MarkdownParser

class Encryptor:

    def __init__(self, password, input_file, output_file, error_correction):
        self.password = password
        self.input_file = input_file
        self.output_file = output_file
        self.error_correction = error_correction
        self.key = Fernet.generate_key()
        self.pdf_writer = PDFWriter(self.output_file)
        self.md_parser = MarkdownParser(self.input_file)

    def generate_key(self):
        # For simplicity, we are using the password as a base for the key.
        # A more secure method would be advised for a production setting.
        self.key = Fernet.generate_key()

    def encrypt_section(self, section):
        cipher_suite = Fernet(self.key)
        return cipher_suite.encrypt(section.encode())

    def process(self):
        self.generate_key()
        sections = self.md_parser.parse_markdown()

        for title, content_parts in sections.items():
            self.pdf_writer.add_section_to_pdf(title, content_parts, self.error_correction)

            # for idx, content in enumerate(content_parts):
            #     section_title = f"{title} (Part {idx + 1})" if len(content_parts) > 1 else title
            #     encrypted_content = self.encrypt_section(content)
            #     # print('------------------')
            #     # print(content)
            #     self.pdf_writer.add_section_to_pdf(section_title, encrypted_content, self.error_correction)

        self.pdf_writer.save()