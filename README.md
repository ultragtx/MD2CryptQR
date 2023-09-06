# MD2CryptQR

## Introduction

**MD2CryptQR** is a powerful tool that transforms your Markdown files into secure, encrypted QR codes, making it simple to share and distribute sensitive text data. The package consists of two main components: a Python-based encryptor and a web-based decryptor for quick and easy viewing.

---

## Table of Contents

- [MD2CryptQR](#md2cryptqr)
    - [Introduction](#introduction)
    - [Table of Contents](#table-of-contents)
    - [Installation](#installation)
        - [Encryptor Installation](#encryptor-installation)
        - [Decryptor Installation](#decryptor-installation)
    - [Usage](#usage)
        - [Encryptor Command Line Options](#encryptor-command-line-options)
        - [Decryptor Usage](#decryptor-usage)

---

## Installation

### Encryptor Installation

1. To install the encryptor, first download the source code from GitHub or clone the repository.
2. Open your terminal, navigate to the encryptor-py directory, and run:

    ```bash
    cd encryptor-py
    pip install -r requirements.txt
    ```

### Decryptor Installation

* Option 1: Access the online version at https://ultragtx.github.io/MD2CryptQR/index.html

* Option 2, build and serve these static files on a private *HTTPS* server.

    ```bash
    cd decryptor
    npm install
    npm run build
    ```

---

## Usage

### Encryptor Command Line Options

Navigate to the folder containing your Markdown file and execute the following command:

```bash
python encryptor/main.py [OPTIONS]
```

Here are the available options:

- `-i`, `--input`: **(Required)** Input Markdown file path.
- `-o`, `--output`: Output PDF file path. Default is `output.pdf`.
- `-e`, `--error_correction`: Level of QR error correction. Options are `L`, `M`, `Q`, `H`. Default is `L`.
- `-l`, `--qr_data_length`: The data length for each QR code. Default is `700`.
- `-c`, `--compact_mode`: Enable compact mode. In this mode, The encryptor will not split the content into sections based on Markdown title syntax, and will not print titles for each section.

**Example:**

```bash
python encryptor/main.py -i ../README.md -o ../sample-output/output-compact.pdf -e M -l 700 -c
```

You can find sample PDF outputs in both standard and compact modes in the repository. Click the links below to view or download them:

- [Sample Output in Standard Mode](https://github.com/ultragtx/MD2CryptQR/blob/main/sample-output/output.pdf)
- [Sample Output in Compact Mode](https://github.com/ultragtx/MD2CryptQR/blob/main/sample-output/output-compact.pdf)

### Decryptor Usage

1. Go to the web-based decryptor, either hosted on GitHub or your private HTTPS server.
2. Input the password used during encryption.
3. Scan each QR code in the generated document.

---

Thank you for using **MD2CryptQR**. For further assistance, please visit our GitHub repository.
