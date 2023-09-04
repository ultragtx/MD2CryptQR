import re

class MarkdownParser:

    def __init__(self, input_file, max_qr_data_length=800):
        self.input_file = input_file
        self.max_qr_data_length = max_qr_data_length  # Maximum characters that can be stored in a single QR code

    def _split_large_section(self, content):
        parts = []
        current_part = ""
        for line in content.split("\n"):
            # Markdown code block or table starts
            if line.startswith("```") or line.startswith("|"):
                if len(current_part) + len(line) > self.max_qr_data_length:
                    parts.append(current_part)
                    current_part = ""
                current_part += line + "\n"
                continue
            
            # Append line to current part, check length
            if len(current_part) + len(line) + 1 > self.max_qr_data_length:  # +1 for the newline character
                parts.append(current_part)
                current_part = ""
            current_part += line + "\n"
        parts.append(current_part)
        return parts

    def parse_markdown(self):
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regular expression to match Markdown headers, from `# Title` to `###### Title`
        sections = re.split(r'(^#{1,6} .+)', content, flags=re.M)[1:]

        # print('--=--------------')
        # print(len(sections))
        # print(sections[0])
        # print('-')
        # print(sections[1])

        # Organize sections into a dictionary
        section_dict = {}
        i = 0
        while i < len(sections):
            title = sections[i].strip().replace("\n", "")
            i += 1  # Move to the next element, potentially content
            
            content = ''
            if i < len(sections) and not re.match(r'^#{1,6} .+', sections[i]):  # Check if it's not another title
                content = sections[i].strip()
                i += 1  # Move to the next element, potentially the next title

            # Split large section content into multiple parts
            if len(content) > self.max_qr_data_length:
                print('!!!!!!lenth exceeds:', len(content))
                content_parts = self._split_large_section(content)
                section_dict[title] = content_parts
            else:
                section_dict[title] = [content]

        return section_dict
