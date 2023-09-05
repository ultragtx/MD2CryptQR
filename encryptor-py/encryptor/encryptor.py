from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import hashlib
import json
from pdf_writer import PDFWriter
from markdown_parser import MarkdownParser
import binascii


def pkcs7_padding(data, block_size=16):
    pad_len = block_size - len(data) % block_size
    return data + bytes([pad_len] * pad_len)

class Encryptor:

    def __init__(self, password, input_file, output_file, error_correction):
        self.password_hash = hashlib.sha256(password.encode()).digest()
        
        self.salt = self.password_hash[:8]
        self.key_material = self.password_hash[8:24]
        self.iv = self.password_hash[16:]

        self.input_file = input_file
        self.output_file = output_file
        self.error_correction = error_correction
        self.backend = default_backend()
        self.pdf_writer = PDFWriter(self.output_file)
        self.md_parser = MarkdownParser(self.input_file)

    def generate_key(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=self.backend
        )
        self.key = kdf.derive(self.key_material)
        
        # Checked!
        # print("Salt in Hex: ", binascii.hexlify(self.salt).decode())
        # print("Key Material in Hex: ", binascii.hexlify(self.key_material).decode())
        # print("IV in Hex: ", binascii.hexlify(self.iv).decode())
        # print("Key in Hex: ", binascii.hexlify(self.key))

    def encrypt_chunk(self, chunk):
        encryptor = Cipher(
            algorithms.AES(self.key),
            modes.CBC(self.iv[:16]),  # Use 16 bytes for CBC IV
            backend=self.backend
        ).encryptor()

        chunk_str = json.dumps(chunk, ensure_ascii=False).encode('utf-8')
        padded_data = pkcs7_padding(chunk_str)
        ct = encryptor.update(padded_data) + encryptor.finalize()

        # print("Chunk in Hex: ", binascii.hexlify(ct))
        # print(ct[0])
        # print(ct[1])
        # print(ct[2])
        # print(ct[3])

        return ct

    def process(self):
        self.generate_key()
        sections = self.md_parser.parse_markdown()

        # sections = sections[:1] # for debugging

        for section in sections:
            encrypted_chunks = []
            title = section[0]["title"]
            idx = section[0]["idx"]

            for chunk in section:
                # chunk_str = json.dumps(chunk, ensure_ascii=False)
                
                encrypted_content = self.encrypt_chunk(chunk)
                encrypted_chunks.append(encrypted_content)
                # encrypted_chunks.append(chunk_str)
            
            self.pdf_writer.add_section_to_pdf(title, encrypted_chunks, self.error_correction)

        self.pdf_writer.save()
