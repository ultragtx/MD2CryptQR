import argparse
from getpass import getpass  # Import the getpass library
from encryptor import Encryptor

def parse_args():
    parser = argparse.ArgumentParser(description="Encrypt and print Markdown to PDF as QR Codes.")
    # parser.add_argument("-p", "--password", required=True, help="Password for encryption")
    parser.add_argument("-i", "--input", required=True, help="Input markdown file path")
    parser.add_argument("-o", "--output", default="output.pdf", help="Output PDF file path")
    parser.add_argument("-e", "--error_correction", default="L", choices=['L', 'M', 'Q', 'H'], help="Level of error correction")
    parser.add_argument('-l', "--qr_data_length", type=int, default=700, help='The data lengh for each qr code')
    parser.add_argument("-c", '--compact_mode', action='store_true', help="Compact mode. Will not split the content into sections based on Markdown title syntax, and will not print titles for each section")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # Prompt the user for the password
    password = getpass("Please enter the encryption password: ")

    encryptor = Encryptor(password, args.input, args.output, args.error_correction, args.qr_data_length, args.compact_mode)
    encryptor.process()
