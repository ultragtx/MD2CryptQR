import argparse
from encryptor import Encryptor

def parse_args():
    parser = argparse.ArgumentParser(description="Encrypt and print Markdown to PDF as QR Codes.")
    parser.add_argument("-p", "--password", required=True, help="Password for encryption")
    parser.add_argument("-i", "--input", required=True, help="Input markdown file path")
    parser.add_argument("-o", "--output", default="output.pdf", help="Output PDF file path")
    parser.add_argument("-e", "--error_correction", default="L", choices=['L', 'M', 'Q', 'H'], help="Level of error correction")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    encryptor = Encryptor(args.password, args.input, args.output, args.error_correction)
    encryptor.process()
