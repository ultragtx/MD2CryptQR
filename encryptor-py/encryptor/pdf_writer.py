from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import qrcode
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import binascii

# Register the font (only need to do this once)
font_path = "./fonts/Arial Unicode.ttf"
font_name = "ArialUnicode";
pdfmetrics.registerFont(TTFont(font_name, font_path))

class PDFWriter:
    
    def __init__(self, path, compact_mode):
        self.path = path
        self.compact_mode = compact_mode
        self.c = canvas.Canvas(self.path, pagesize=A4)
        
        self.title_font_size = 10
        self.content_font_size = 8

        self.c.setFont(font_name, self.content_font_size)  # Use as a default font

        self.page_width, self.page_height = A4
        self.margin = 1 * cm  # Page margin
        self.current_height = self.page_height - self.margin  # Start 2 cm from the top
        self.current_width = self.margin  # Start 2 cm from the left
        self.qr_size = 6.3 * cm  # Size of each QR code, 4 cm x 4 cm
        self.margin_between_qr = 0 * cm  # Margin between each QR code
        self.row_spacing = 0.5 * cm
        self.title_height = 0 if compact_mode else 0.6 * cm  # Height reserved for title
        self.content_line_height = 0.4 * cm  # Height reserved for content

    def add_section_to_pdf(self, title, startIdx, encrypted_content, error_correction):
        # Print section title
        # print(title, len(encrypted_content))
        # print('=-=-=-=-')
        self.c.setFontSize(self.title_font_size)
        if not self.compact_mode:
            self.c.drawString(self.current_width, self.current_height, title)
        self.c.setFontSize(self.content_font_size)
        self.current_height -= self.title_height + self.qr_size + self.content_line_height  # Adjust vertical position

        # Loop through each chunk of encrypted content for this section
        for sequence_number, content_chunk in enumerate(encrypted_content):
            # print(content_chunk[:10], '|', len(content_chunk))
            # Generate QR Codes and add to PDF
            qr = qrcode.QRCode(
                version=None,  # Let the library auto-determine
                error_correction=getattr(qrcode.constants, f'ERROR_CORRECT_{error_correction}'),
                box_size=10,
                border=4,
            )

            # print('-----------len of encrypted_content: ', len(content_chunk.encode('utf-8'))),
            # print('-----------len of encrypted_content: ', len(content_chunk))

            print('Print chunk: %2d, length: %d' % (startIdx + sequence_number, len(content_chunk)))

            # print("Chunk in Hex: ", binascii.hexlify(content_chunk))

            qr.add_data(content_chunk)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            # Use ImageReader to read the BytesIO stream
            image = ImageReader(buffer)

            # Check if we need to create a new row or page
            if self.current_height < self.margin:
                self.c.showPage()  # create new page
                self.c.setFont(font_name, self.content_font_size)
                self.current_height = self.page_height - self.margin - self.content_line_height - self.qr_size   # Reset to top, and leave enough space for the qr code
                self.current_width = self.margin  # Reset to left margin

            if self.current_width + self.qr_size + self.margin > self.page_width:
                self.current_height -= self.qr_size + self.row_spacing  # Move to next row
                self.current_width = self.margin  # Reset to left margin

            if self.current_height < self.margin:
                self.c.showPage()  # create new page
                self.c.setFont(font_name, self.content_font_size)
                self.current_height = self.page_height - self.margin - self.content_line_height - self.qr_size   # Reset to top, and leave enough space for the qr code
                self.current_width = self.margin  # Reset to left margin

            # Draw sequence number and QR code to PDF
            self.c.drawString(self.current_width, self.current_height, f"Index: {startIdx + sequence_number}")
            # self.c.drawString(self.current_width, self.current_height + self.content_line_height, f"Con: {content_chunk[:10]}")
            self.c.drawImage(image, self.current_width, self.current_height + self.content_line_height, width=self.qr_size, height=self.qr_size)

            # Update position for next QR code in the same row
            self.current_width += self.qr_size + self.margin_between_qr  # Adjust horizontal position

        # Update position for next section
        self.current_width = self.margin  # Reset to left margin
        self.current_height -= self.title_height

        # Check if we need to create a new row or page
        if self.current_height - self.qr_size < self.margin:
            self.c.showPage()  # create new page
            self.c.setFont(font_name, self.content_font_size)
            self.current_height = self.page_height - self.margin  # Reset to top
            self.current_width = self.margin  # Reset to left margin

    def save(self):
        self.c.save()
