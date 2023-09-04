from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import qrcode
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register the font (only need to do this once)
font_path = "./fonts/Arial Unicode.ttf"
font_name = "ArialUnicode";
pdfmetrics.registerFont(TTFont(font_name, font_path))

class PDFWriter:
    
    def __init__(self, path):
        self.path = path
        self.c = canvas.Canvas(self.path, pagesize=A4)
        
        self.title_font_size = 10
        self.content_font_size = 8

        self.c.setFont(font_name, self.content_font_size)  # Use as a default font

        self.page_width, self.page_height = A4
        self.current_height = self.page_height - 2 * cm  # Start 2 cm from the top
        self.current_width = 2 * cm  # Start 2 cm from the left
        self.qr_size = 6 * cm  # Size of each QR code, 4 cm x 4 cm
        self.margin = 2 * cm  # Margin between QR codes
        self.title_height = 0.8 * cm  # Height reserved for title
        self.content_line_height = 0.4 * cm  # Height reserved for content
        self.qr_per_row = int((self.page_width - 2 * cm) // (self.qr_size + self.margin))

    def add_section_to_pdf(self, title, encrypted_content, error_correction):
        # Print section title
        print(title, len(encrypted_content))
        print('=-=-=-=-')
        self.c.setFontSize(self.title_font_size)
        self.c.drawString(self.current_width, self.current_height, title)
        self.c.setFontSize(self.content_font_size)
        self.current_height -= self.title_height + self.qr_size + self.content_line_height  # Adjust vertical position

        # Loop through each chunk of encrypted content for this section
        for sequence_number, content_chunk in enumerate(encrypted_content):
            print(content_chunk[:10], '|', len(content_chunk))
            # Generate QR Codes and add to PDF
            qr = qrcode.QRCode(
                version=None,  # Let the library auto-determine
                error_correction=getattr(qrcode.constants, f'ERROR_CORRECT_{error_correction}'),
                box_size=10,
                border=4,
            )

            print('-----------len of encrypted_content: ', len(content_chunk))

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
                self.current_height = self.page_height - self.margin  # Reset to top
                self.current_width = self.margin  # Reset to left margin

            if self.current_width + self.qr_size + self.margin > self.page_width:
                self.current_height -= self.qr_size + 1 * cm  # Move to next row
                self.current_width = self.margin  # Reset to left margin

            # Draw sequence number and QR code to PDF
            self.c.drawString(self.current_width, self.current_height, f"Seq: {sequence_number + 1}")
            # self.c.drawString(self.current_width, self.current_height + self.content_line_height, f"Con: {content_chunk[:10]}")
            self.c.drawImage(image, self.current_width, self.current_height + self.content_line_height, width=self.qr_size, height=self.qr_size)

            # Update position for next QR code in the same row
            self.current_width += self.qr_size + 1 * cm  # Adjust horizontal position

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
